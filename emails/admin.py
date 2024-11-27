from django.contrib import admin
from .models import IMAPServer, Email

@admin.register(IMAPServer)
class IMAPServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'username', 'user', 'sync_limit_type', 'last_sync')
    list_filter = ('use_ssl', 'user', 'sync_limit_type', 'exclude_trash')
    search_fields = ('name', 'host', 'username', 'folders_to_sync')
    ordering = ('name',)
    fieldsets = (
        (None, {
            'fields': ('user', 'name', 'host', 'port', 'username', 'password', 'use_ssl')
        }),
        ('Sync Settings', {
            'fields': ('sync_limit_type', 'sync_limit_value', 'folders_to_sync', 'exclude_trash')
        }),
        ('Status', {
            'fields': ('last_sync',)
        }),
    )

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'recipient', 'date', 'folder', 'user', 'thread_status')
    list_filter = ('imap_server', 'date', 'user', 'folder')
    search_fields = ('subject', 'sender', 'recipient', 'body_text', 'message_id', 'thread_id')
    ordering = ('-date',)
    date_hierarchy = 'date'
    readonly_fields = ('thread_id', 'in_reply_to', 'references', 'message_id', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'imap_server', 'folder', 'subject', 'sender', 'recipient', 'date')
        }),
        ('Content', {
            'fields': ('body_text', 'body_html')
        }),
        ('Threading Information', {
            'fields': ('thread_id', 'in_reply_to', 'references'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('message_id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def thread_status(self, obj):
        """Display thread status in admin list view"""
        if not obj.thread_id:
            return "Single"
        thread_count = Email.objects.filter(thread_id=obj.thread_id).count()
        return f"Thread ({thread_count} messages)"
    thread_status.short_description = 'Thread Status'

    def get_queryset(self, request):
        """Optimize queryset for admin list view"""
        return super().get_queryset(request).select_related('user', 'imap_server')
