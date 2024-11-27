from django.db import migrations

def set_default_folder(apps, schema_editor):
    Email = apps.get_model('emails', 'Email')
    Email.objects.filter(folder='0').update(folder='INBOX')

class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0002_remove_imapserver_folder_email_folder_and_more'),
    ]

    operations = [
        migrations.RunPython(set_default_folder),
    ]
