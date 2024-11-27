from django.core.management.base import BaseCommand
from django.utils import timezone
from emails.models import IMAPServer, Email
from django.contrib.auth.models import User
import imaplib
import email
from email.header import decode_header
import datetime
import logging
import re
from email.utils import parsedate_to_datetime, getaddresses, make_msgid
import hashlib
from imap_tools import MailBox, AND, MailBoxUnencrypted, MailMessage, A
import html
import chardet
import socket
import ssl

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Synchronize emails from configured IMAP servers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=int,
            help='Sync emails for specific user ID',
        )

    def handle(self, *args, **options):
        try:
            if options['user']:
                users = User.objects.filter(id=options['user'])
                if not users.exists():
                    self.stderr.write(f"User with ID {options['user']} not found")
                    return
            else:
                users = User.objects.all()

            for user in users:
                self.stdout.write(f"Processing servers for user: {user.username}")
                servers = IMAPServer.objects.filter(user=user)
                
                for server in servers:
                    try:
                        self.sync_server(server)
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Successfully synced server: {server.name}"
                            )
                        )
                    except Exception as e:
                        self.stderr.write(
                            self.style.ERROR(
                                f"Error syncing server {server.name}: {str(e)}"
                            )
                        )
                        logger.exception(f"Error syncing server {server.name}")

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Sync failed: {str(e)}"))
            logger.exception("Email sync failed")

    def sync_server(self, server):
        """Sync emails from a specific IMAP server."""
        try:
            # Choose appropriate connection class
            MailBoxClass = MailBox if server.use_ssl else MailBoxUnencrypted
            
            # Set timeout for operations
            socket.setdefaulttimeout(300)  # 5 minutes timeout
            
            # Connect with error handling
            try:
                mailbox = MailBoxClass(server.host, port=server.port)
                mailbox.login(server.username, server.password)
                logger.debug(f"Successfully connected to server {server.name}")
            except ssl.SSLError as e:
                raise Exception(f"SSL connection failed: {str(e)}")
            except socket.timeout:
                raise Exception("Connection timed out")
            except socket.gaierror:
                raise Exception(f"Could not resolve hostname: {server.host}")
            except Exception as e:
                raise Exception(f"Connection failed: {str(e)}")

            try:
                # Get list of folders
                folders_to_sync = self._get_folders_to_sync(mailbox, server)
                logger.debug(f"Folders to sync: {folders_to_sync}")
                
                for folder in folders_to_sync:
                    try:
                        self._sync_folder(mailbox, server, folder)
                    except Exception as e:
                        logger.error(f"Error syncing folder {folder}: {str(e)}")
                        continue

                # Update last sync time
                server.last_sync = timezone.now()
                server.save()

            finally:
                # Always try to logout
                try:
                    mailbox.logout()
                except:
                    pass

        except Exception as e:
            logger.error(f"Error connecting to server: {str(e)}")
            raise

    def _get_folders_to_sync(self, mailbox, server):
        """Get list of folders to sync based on server configuration."""
        try:
            all_folders = []
            
            # List all folders
            for folder_info in mailbox.folder.list():
                folder_name = folder_info.name
                logger.debug(f"Found folder: {folder_name} with flags: {folder_info.flags}")
                
                # Skip trash folder if exclude_trash is True
                if server.exclude_trash and any(name in folder_name.lower() 
                    for name in ['trash', '[gmail]/trash', 'kosz', 'spam', 'junk']):
                    continue
                all_folders.append(folder_name)

            # If specific folders are configured, use only those
            configured_folders = server.get_folders_list()
            if configured_folders:
                return [f for f in all_folders if f in configured_folders]
            
            return all_folders
        except Exception as e:
            logger.error(f"Error listing folders: {str(e)}")
            raise

    def _sync_folder(self, mailbox, server, folder):
        """Sync emails from a specific folder."""
        try:
            # Try to select folder
            try:
                mailbox.folder.set(folder)
                logger.debug(f"Selected folder: {folder}")
            except Exception as e:
                logger.error(f"Could not select folder {folder}: {str(e)}")
                return

            # Build criteria based on sync limits
            criteria = self._build_search_criteria(server)
            
            try:
                # Fetch messages with error handling
                messages = mailbox.fetch(criteria)
                
                # Convert to list if we need to limit
                if server.sync_limit_type == 'last_n':
                    messages = list(messages)[-server.sync_limit_value:]
                
                for msg in messages:
                    try:
                        self._process_email(msg, server, folder)
                    except Exception as e:
                        logger.error(f"Error processing email in folder {folder}: {str(e)}")
                        continue

            except Exception as e:
                logger.error(f"Error fetching messages from folder {folder}: {str(e)}")
                raise

        except Exception as e:
            logger.error(f"Error accessing folder {folder}: {str(e)}")
            raise

    def _build_search_criteria(self, server):
        """Build search criteria based on server sync settings."""
        if server.sync_limit_type == 'all':
            return None
        
        if server.sync_limit_type == 'last_n':
            return None  # We'll limit after fetching
        
        # Calculate date for time-based limits
        if server.sync_limit_type == 'days':
            delta = datetime.timedelta(days=server.sync_limit_value)
        elif server.sync_limit_type == 'weeks':
            delta = datetime.timedelta(weeks=server.sync_limit_value)
        elif server.sync_limit_type == 'months':
            delta = datetime.timedelta(days=server.sync_limit_value * 30)
        else:
            return None

        date = (timezone.now() - delta).date()
        return A(date_gte=date)

    def _process_email(self, msg, server, folder):
        """Process and save email message."""
        try:
            # Get message headers
            headers = {}
            for header in msg.obj.items():
                headers[header[0].lower()] = header[1]

            # Get references and in-reply-to from headers
            references = headers.get('references', '').split()
            in_reply_to = headers.get('in-reply-to', '')

            # Generate thread ID
            thread_id = self._generate_thread_id(references, in_reply_to, msg)

            # Clean and decode text
            subject = self._clean_text(msg.subject)
            body_text = self._clean_text(msg.text)
            body_html = self._clean_text(msg.html)

            # Create or update email
            email_obj, created = Email.objects.update_or_create(
                message_id=str(msg.uid),
                user=server.user,
                imap_server=server,
                folder=folder,
                defaults={
                    'subject': subject or '(No Subject)',
                    'sender': str(msg.from_) or 'unknown',
                    'recipient': str(msg.to) or 'unknown',
                    'date': msg.date or timezone.now(),
                    'body_text': body_text,
                    'body_html': body_html,
                    'in_reply_to': in_reply_to,
                    'references': ' '.join(references),
                    'thread_id': thread_id
                }
            )

            if created:
                logger.debug(f"Created new email: {subject} in folder {folder}")
            else:
                logger.debug(f"Updated existing email: {subject} in folder {folder}")

        except Exception as e:
            logger.error(f"Error saving email: {str(e)}")
            raise

    def _generate_thread_id(self, references, in_reply_to, msg):
        """Generate a thread ID based on message references or create a new one."""
        if references:
            # Use the first message ID in references as thread ID
            return references[0]
        elif in_reply_to:
            # Use in-reply-to as thread ID
            return in_reply_to
        else:
            # Generate new thread ID based on subject and first few chars of content
            thread_hash = hashlib.md5(f"{msg.subject}{msg.text[:100]}".encode()).hexdigest()
            return f"thread-{thread_hash}"

    def _clean_text(self, text):
        """Clean and decode text, handling various encodings."""
        if not text:
            return ""
        
        if isinstance(text, bytes):
            # Detect encoding
            detected = chardet.detect(text)
            try:
                text = text.decode(detected['encoding'] or 'utf-8', errors='replace')
            except:
                text = text.decode('utf-8', errors='replace')
        
        # Convert HTML entities
        text = html.unescape(text)
        
        # Remove null bytes and other problematic characters
        text = text.replace('\x00', '').replace('\r', '\n')
        
        return text
