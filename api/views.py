from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from emails.models import IMAPServer, Email
from .serializers import (
    IMAPServerSerializer, EmailSerializer, 
    EmailListSerializer, ThreadEmailSerializer
)
from django.utils import timezone
from django.db.models import Q, Count
from imap_tools import MailBox, AND
import datetime
import logging
from emails.management.commands.sync_emails import Command as SyncCommand

logger = logging.getLogger(__name__)

class IMAPServerViewSet(viewsets.ModelViewSet):
    serializer_class = IMAPServerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'host', 'username']

    def get_queryset(self):
        return IMAPServer.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        imap_server = self.get_object()
        sync_command = SyncCommand()
        
        try:
            sync_command.sync_server(imap_server)
            return Response({'status': 'success', 'message': 'Email sync completed'})
        except Exception as e:
            logger.error(f"Error during sync: {str(e)}")
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class EmailViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['imap_server', 'folder', 'date']
    search_fields = ['subject', 'sender', 'recipient', 'body_text']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']

    def get_queryset(self):
        return Email.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return EmailListSerializer
        return EmailSerializer

    @action(detail=False)
    def threads(self, request):
        """Get all email threads"""
        threads = (
            Email.objects
            .filter(user=self.request.user)
            .exclude(thread_id='')
            .values('thread_id')
            .distinct()
        )
        
        thread_emails = []
        for thread in threads:
            thread_id = thread['thread_id']
            emails = (
                Email.objects
                .filter(thread_id=thread_id)
                .order_by('date')
            )
            if emails:
                thread_emails.append(emails[0])  # Add the first email of each thread

        serializer = EmailListSerializer(thread_emails, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def thread(self, request, pk=None):
        """Get all emails in a thread"""
        email_obj = self.get_object()
        if not email_obj.thread_id:
            return Response([EmailSerializer(email_obj).data])
        
        thread_emails = (
            Email.objects
            .filter(thread_id=email_obj.thread_id)
            .order_by('date')
        )
        serializer = EmailSerializer(thread_emails, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def folders(self, request):
        """Get list of available folders"""
        folders = (
            Email.objects
            .filter(user=self.request.user)
            .values_list('folder', flat=True)
            .distinct()
            .order_by('folder')
        )
        return Response(list(folders))

    @action(detail=False)
    def statistics(self, request):
        """Get email statistics"""
        total_emails = Email.objects.filter(user=self.request.user).count()
        total_threads = (
            Email.objects
            .filter(user=self.request.user)
            .exclude(thread_id='')
            .values('thread_id')
            .distinct()
            .count()
        )
        folders_count = (
            Email.objects
            .filter(user=self.request.user)
            .values('folder')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        return Response({
            'total_emails': total_emails,
            'total_threads': total_threads,
            'folders': {
                item['folder']: item['count'] 
                for item in folders_count
            }
        })
