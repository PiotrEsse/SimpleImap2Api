from rest_framework import serializers
from emails.models import IMAPServer, Email
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class IMAPServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = IMAPServer
        fields = (
            'id', 'name', 'host', 'port', 'username', 'password',
            'use_ssl', 'sync_limit_type', 'sync_limit_value',
            'folders_to_sync', 'exclude_trash', 'last_sync'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'last_sync': {'read_only': True}
        }

    def validate(self, data):
        """Validate the IMAP server configuration."""
        # Validate sync limit value
        sync_limit_type = data.get('sync_limit_type')
        sync_limit_value = data.get('sync_limit_value')
        
        if sync_limit_type != 'all' and not sync_limit_value:
            raise serializers.ValidationError({
                'sync_limit_value': 'Sync limit value is required for this sync type'
            })
        
        if sync_limit_value and sync_limit_value < 1:
            raise serializers.ValidationError({
                'sync_limit_value': 'Sync limit value must be positive'
            })

        # Clean folders list
        folders_to_sync = data.get('folders_to_sync', '')
        if folders_to_sync:
            folders = [f.strip() for f in folders_to_sync.split(',') if f.strip()]
            data['folders_to_sync'] = ','.join(folders)

        return data

    def update(self, instance, validated_data):
        """Update IMAP server instance."""
        # Don't update password if not provided
        if 'password' not in validated_data:
            validated_data.pop('password', None)
        return super().update(instance, validated_data)

class ThreadEmailSerializer(serializers.ModelSerializer):
    """Serializer for emails within a thread"""
    class Meta:
        model = Email
        fields = (
            'id', 'subject', 'sender', 'recipient',
            'date', 'body_text', 'body_html', 'folder'
        )

class EmailSerializer(serializers.ModelSerializer):
    thread_emails = serializers.SerializerMethodField()
    
    class Meta:
        model = Email
        fields = (
            'id', 'message_id', 'subject', 'sender', 'recipient',
            'date', 'body_text', 'body_html', 'folder', 'created_at',
            'updated_at', 'thread_id', 'in_reply_to', 'thread_emails'
        )
        read_only_fields = (
            'created_at', 'updated_at', 'thread_id',
            'in_reply_to', 'thread_emails'
        )

    def get_thread_emails(self, obj):
        """Get all emails in the same thread, excluding the current one"""
        if not obj.thread_id:
            return []
        
        thread_emails = (Email.objects
                        .filter(thread_id=obj.thread_id)
                        .exclude(id=obj.id)
                        .order_by('date'))
        
        return ThreadEmailSerializer(thread_emails, many=True).data

class EmailListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list view"""
    thread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Email
        fields = (
            'id', 'subject', 'sender', 'recipient',
            'date', 'folder', 'thread_id', 'thread_count'
        )

    def get_thread_count(self, obj):
        """Get the number of emails in the thread"""
        if not obj.thread_id:
            return 1
        return Email.objects.filter(thread_id=obj.thread_id).count()
