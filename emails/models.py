from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class IMAPServer(models.Model):
    SYNC_LIMIT_CHOICES = [
        ('all', 'All Messages'),
        ('last_n', 'Last N Messages'),
        ('days', 'Messages from Last N Days'),
        ('weeks', 'Messages from Last N Weeks'),
        ('months', 'Messages from Last N Months'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='imap_servers'
    )
    name = models.CharField(_('Server Name'), max_length=100)
    host = models.CharField(_('Host'), max_length=255)
    port = models.IntegerField(_('Port'), default=993)
    username = models.CharField(_('Username'), max_length=255)
    password = models.CharField(_('Password'), max_length=255)
    use_ssl = models.BooleanField(_('Use SSL'), default=True)
    
    # Sync settings
    sync_limit_type = models.CharField(
        _('Sync Limit Type'),
        max_length=20,
        choices=SYNC_LIMIT_CHOICES,
        default='all'
    )
    sync_limit_value = models.IntegerField(
        _('Sync Limit Value'),
        null=True,
        blank=True,
        help_text=_('Number of messages or time period to sync')
    )
    
    # Folder settings
    folders_to_sync = models.TextField(
        _('Folders to Sync'),
        blank=True,
        help_text=_('Comma-separated list of folders to sync. Leave empty for all folders except trash.')
    )
    exclude_trash = models.BooleanField(
        _('Exclude Trash'),
        default=True,
        help_text=_('Exclude trash folder from syncing')
    )
    
    last_sync = models.DateTimeField(_('Last Sync'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('IMAP Server')
        verbose_name_plural = _('IMAP Servers')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.username})"

    def get_folders_list(self):
        """Returns list of folders to sync"""
        if not self.folders_to_sync.strip():
            return []
        return [f.strip() for f in self.folders_to_sync.split(',')]

class Email(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='emails'
    )
    imap_server = models.ForeignKey(
        IMAPServer,
        on_delete=models.CASCADE,
        related_name='emails'
    )
    message_id = models.CharField(
        _('Message ID'),
        max_length=255,
        help_text=_('Unique identifier for the email')
    )
    subject = models.CharField(_('Subject'), max_length=1000, blank=True)
    sender = models.CharField(_('Sender'), max_length=255)
    recipient = models.CharField(_('Recipient'), max_length=255)
    date = models.DateTimeField(_('Date'))
    body_text = models.TextField(_('Body Text'), blank=True)
    body_html = models.TextField(_('Body HTML'), blank=True)
    raw_headers = models.TextField(_('Raw Headers'), blank=True)
    
    # Threading fields
    in_reply_to = models.CharField(_('In Reply To'), max_length=255, blank=True, null=True)
    references = models.TextField(_('References'), blank=True)
    thread_id = models.CharField(_('Thread ID'), max_length=255, blank=True, null=True)
    
    # Folder information
    folder = models.CharField(_('Folder'), max_length=255)
    
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Email')
        verbose_name_plural = _('Emails')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['message_id']),
            models.Index(fields=['date']),
            models.Index(fields=['sender']),
            models.Index(fields=['subject']),
            models.Index(fields=['thread_id']),
            models.Index(fields=['folder']),
        ]
        unique_together = [['user', 'imap_server', 'message_id', 'folder']]

    def __str__(self):
        return f"{self.subject} ({self.date})"

    def get_thread(self):
        """Returns all emails in the same thread"""
        if not self.thread_id:
            return Email.objects.filter(id=self.id)
        return Email.objects.filter(thread_id=self.thread_id).order_by('date')
