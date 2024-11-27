from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q, Count, Max, F
from datetime import datetime
from .models import IMAPServer, Email

@login_required
def email_list(request):
    # Get query parameters
    server_id = request.GET.get('server')
    folder = request.GET.get('folder')
    search_query = request.GET.get('q')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    show_threads = request.GET.get('show_threads') == 'on'

    # Base queryset
    emails = Email.objects.filter(user=request.user)

    # Apply filters
    if server_id:
        emails = emails.filter(imap_server_id=server_id)
    
    if folder:
        emails = emails.filter(folder=folder)
    
    if search_query:
        emails = emails.filter(
            Q(subject__icontains=search_query) |
            Q(sender__icontains=search_query) |
            Q(recipient__icontains=search_query) |
            Q(body_text__icontains=search_query)
        )
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            emails = emails.filter(date__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            emails = emails.filter(date__lte=date_to)
        except ValueError:
            pass

    # Handle thread grouping
    if show_threads:
        # Get the latest email from each thread
        thread_emails = emails.exclude(thread_id='').values('thread_id').annotate(
            latest_date=Max('date'),
            count=Count('id')
        ).filter(count__gt=1)
        
        thread_ids = [t['thread_id'] for t in thread_emails]
        
        # Get the latest email from each thread and non-threaded emails
        emails = (emails.filter(
            Q(thread_id='') |  # Non-threaded emails
            Q(thread_id__in=thread_ids, date__in=[t['latest_date'] for t in thread_emails])  # Latest from threads
        ))

    # Add thread count for display
    emails = emails.annotate(
        thread_count=Count(
            'thread_id',
            filter=Q(thread_id=F('thread_id')) & ~Q(thread_id='')
        )
    )

    # Order by date
    emails = emails.order_by('-date')

    # Get all available folders for filtering
    folders = Email.objects.filter(
        user=request.user
    ).values_list('folder', flat=True).distinct().order_by('folder')

    context = {
        'emails': emails,
        'imap_servers': IMAPServer.objects.filter(user=request.user),
        'selected_server': int(server_id) if server_id else None,
        'selected_folder': folder,
        'folders': folders,
        'show_threads': show_threads
    }
    return render(request, 'emails/email_list.html', context)

@login_required
def imap_server_list(request):
    context = {
        'imap_servers': IMAPServer.objects.filter(user=request.user)
    }
    return render(request, 'emails/imap_server_list.html', context)
