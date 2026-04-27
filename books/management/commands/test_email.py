from django.core.management.base import BaseCommand
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
import sys

class Command(BaseCommand):
    help = 'Test email configuration by sending a test email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            help='Email address to send test email to',
            required=True
        )

    def handle(self, *args, **options):
        recipient_email = options['to']
        
        self.stdout.write('🚀 Testing email configuration...\n')
        
        # Print current configuration (without password)
        self.stdout.write(f"📧 EMAIL_HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"📧 EMAIL_PORT: {settings.EMAIL_PORT}")
        self.stdout.write(f"📧 EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"📧 EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"📧 DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write(f"📧 Sending to: {recipient_email}\n")
        
        try:
            # Test with simple send_mail
            self.stdout.write("📨 Testing simple email...")
            result = send_mail(
                subject='[Test] Django Email Configuration Test',
                message='This is a test email from Django. If you receive this, your email configuration is working correctly!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False
            )
            
            if result:
                self.stdout.write(self.style.SUCCESS('✅ Simple email sent successfully!'))
            else:
                self.stdout.write(self.style.ERROR('❌ Failed to send simple email'))
                return
            
            # Test with EmailMessage (more advanced)
            self.stdout.write("📨 Testing advanced email...")
            email = EmailMessage(
                subject='[Test] Advanced Django Email Test',
                body='This is an advanced test email using EmailMessage class. Configuration is working!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],
                reply_to=[settings.EMAIL_HOST_USER]
            )
            email.send()
            
            self.stdout.write(self.style.SUCCESS('✅ Advanced email sent successfully!'))
            self.stdout.write(self.style.SUCCESS('🎉 All email tests passed! Check your inbox.'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Email test failed: {str(e)}'))
            self.stdout.write('\n🔧 Common solutions:')
            self.stdout.write('1. Check if 2FA is enabled in Gmail')
            self.stdout.write('2. Use App Password (not your regular password)')
            self.stdout.write('3. Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env')
            self.stdout.write('4. Verify Gmail account settings allow less secure apps')
            sys.exit(1)