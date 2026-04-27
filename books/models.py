from django.db import models, transaction
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

# Create your models here.

from django.utils.translation import gettext_lazy as _

class Author(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    birth_date = models.DateField(null=True, blank=True, verbose_name=_("Date of Birth"))
    nationality = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Nationality"))

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")

class Publisher(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name of Publisher"))
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Address"))
    website = models.URLField(null=True, blank=True, verbose_name=_("Website"))

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = _("Publisher")
        verbose_name_plural = _("Publishers")

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Tag"))

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    author = models.ManyToManyField(Author,verbose_name=_("Author"))
    isbn = models.CharField(max_length=13, unique=True, verbose_name=_("ISBN"))
    publication_date = models.DateField(verbose_name=_("Publication Date"))
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, verbose_name=_("Publisher"))
    pages = models.PositiveIntegerField(verbose_name=_("Number of Pages"))
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_("Tags"))  # Ex: fiction, non-fiction, science, history
    # Additional book fields
    language = models.CharField(max_length=50, default='English', verbose_name=_("Language"))
    edition = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Edition"))
    description = models.TextField(blank=True, verbose_name=_("Description/Summary"))
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True, verbose_name=_("Cover Image"))
    # Fields for approval system
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='books_created',
        verbose_name=_("Created by"),
        help_text=_("User who created this book entry")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    
    APPROVAL_STATUS_CHOICES = [
        ('pending', _("Pending Approval")),
        ('approved', _("Approved")),
        ('rejected', _("Rejected")),
    ]
    approval_status = models.CharField(
        max_length=20, 
        choices=APPROVAL_STATUS_CHOICES, 
        default='pending',
        verbose_name=_("Approval Status")
    )
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books_approved',
        verbose_name=_("Approved by"),
        help_text=_("Librarian who approved this book")
    )
    approved_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_("Approved at")
    )
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Rejection Reason"),
        help_text=_("Reason for rejection if status is rejected")
    )

    def __str__(self):
        authors = self.author.all()
        if authors.count() == 0:
            return self.title
        elif authors.count() == 1:
            return f"{self.title} - {authors[0].name}"
        else:
            return f"{self.title} - {authors[0].name} et al."
    
    def approve(self, user):
        """Método para aprobar un libro"""
        if user.groups.filter(name='librarian').exists():
            self.approval_status = 'approved'
            self.approved_by = user
            self.approved_at = timezone.now()
            self.save()
            return True
        return False
    
    def reject(self, user, reason=""):
        """Método para rechazar un libro"""
        if user.groups.filter(name='librarian').exists():
            self.approval_status = 'rejected'
            self.approved_by = user
            self.approved_at = timezone.now()
            self.rejection_reason = reason
            self.save()
            return True
        return False
    
    def can_be_used_in_library_items(self):
        """Verifica si el libro puede ser usado para crear LibraryBookItems"""
        return self.approval_status == 'approved'
    
    class Meta:
        verbose_name = _("Book")
        verbose_name_plural = _("Books")
        ordering = ['-created_at']
        # Define custom permission here:
        permissions = [
            ("can_approve_book", "Can approve or reject books"),
        ]
    
class Country(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Country"))

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("City"))
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities", verbose_name=_("Country"))

    def __str__(self):
        return f"{self.name} ({self.country})"

    class Meta:
        unique_together = ('name', 'country')
        verbose_name = _("City")
        verbose_name_plural = _("Cities")

class Library(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Library Name"))
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name=_("City"))
    address = models.CharField(max_length=255, verbose_name=_("Address"))
    email = models.EmailField(null=True, blank=True, verbose_name=_("Email"))
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name=_("Phone Number"))

    def __str__(self):
        return f"{self.name} ({self.city})"

    class Meta:
        verbose_name = _("Library")
        verbose_name_plural = _("Libraries")

class UserProfile(models.Model):
    """
    Extende el modelo User para asignar bibliotecas a usuarios
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    assigned_libraries = models.ManyToManyField(
        Library, 
        blank=True, 
        verbose_name=_("Assigned Libraries"),
        help_text=_("Libraries assigned to this user for managing book items")
    )

    def __str__(self):
        count = self.assigned_libraries.count()
        return f"{self.user.username} - {count} " + _('assigned libraries')

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")
        

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a profile when a user is created
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the profile when the user is saved
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()

class LibraryBookItem(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE, verbose_name=_("Library"))
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name=_("Book"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Inventory Code"))  # Inventory code
    STATUS_CHOICES = [
        ('available', _("Available")),
        ('loaned', _("Loaned")),
        ('reserved', _("Reserved")),
        ('lost', _("Lost")),
        # Add more statuses if needed
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name=_("Status"))
    
    # Audit fields
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='library_items_created',
        verbose_name=_("Created by")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    def __str__(self):
        return f"{self.book.title} ({self.code}) en {self.library.name} - {self.get_status_display()}"

    # Inside LibraryBookItem class in models.py
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.book and not self.book.can_be_used_in_library_items():
            raise ValidationError(_("Only approved books can be added to library inventory"))
        
        # Only validate if we already have the user (avoids error in initial form)
        if self.created_by and not self.created_by.is_superuser:
            user_profile = getattr(self.created_by, 'profile', None)
            if user_profile and not user_profile.assigned_libraries.filter(id=self.library.id).exists():
                raise ValidationError(_("You can only add items to your assigned libraries"))
        def __str__(self):
            return f"{self.book.title} ({self.code}) en {self.library.name} - {self.get_status_display()}"
        
        class Meta:
            verbose_name = _("Library Book Item")
            verbose_name_plural = _("Library Book Items")
            ordering = ['-created_at']   
    
class Reservation(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    email = models.EmailField(verbose_name=_("Email"))
    items = models.ManyToManyField(LibraryBookItem, verbose_name=_("Reserved Items"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    status_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Status Date"))
    STATUS_CHOICES = [
        ('pending', _("Pending")),
        ('ready', _("Ready for Pickup")),
        ('completed', _("Completed")),
        ('canceled', _("Canceled")),
        ('delivered', _("Delivered")),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Status"))
    library = models.ForeignKey(Library, on_delete=models.CASCADE, verbose_name=_("Library"))

    def send_notification(self):
        """
        Send email to user with copy to library.
        All texts are in English and marked for translation.
        """
        # Get library from first item
        first_item = self.items.first()
        if not first_item:
            return

        # Use the library from the reservation (not from items)
        library = self.library
        library_email = library.email or settings.DEFAULT_FROM_EMAIL
        
        # Translatable subject
        subject = _("[%(lib_name)s] Reservation Update: %(status)s") % {
            'lib_name': library.name,
            'status': self.get_status_display()
        }

        # Message dictionary in English (marked for translation)
        messages = {
            'pending': _("Your reservation at %(lib_name)s has been received and is being processed.") % {'lib_name': library.name},
            'ready': _("Your books are ready for pickup! Please visit us at: %(address)s, %(city)s.") % {
                'address': library.address, 
                'city': library.city.name
            },
            'delivered': _("The books have been successfully delivered. Enjoy your reading!"),
            'canceled': _("Your reservation has been canceled."),
            'completed': _("The books have been returned. Thank you for using our library!"),
        }

        body_text = messages.get(self.status, _("Your reservation status has changed to: %(status)s") % {'status': self.get_status_display()})

        try:
            email = EmailMessage(
                subject=subject,
                body=body_text,
                from_email=f"{library.name} <{settings.EMAIL_HOST_USER}>",
                to=[self.email],
                reply_to=[library_email],  # User replies go to library
                cc=[library_email],       # Library gets copy of every movement
            )
            # Don't use fail_silently=True during development/debugging
            email.send(fail_silently=False)
            print(f"✅ Email sent successfully to {self.email} for reservation #{self.id}")
        except Exception as e:
            # Log the error for debugging
            print(f"❌ Failed to send email to {self.email} for reservation #{self.id}: {str(e)}")
            # In production, consider using proper logging:
            # import logging
            # logger = logging.getLogger(__name__)
            # logger.error(f"Failed to send email: {str(e)}")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            is_new = self.pk is None
            status_changed = False
            
            if not is_new:
                old_instance = Reservation.objects.get(pk=self.pk)
                if old_instance.status != self.status:
                    status_changed = True
                    self.status_date = timezone.now()
            else:
                self.status_date = timezone.now()
                status_changed = True # Notificar creación

            # Guardamos la reserva
            super().save(*args, **kwargs)

            # Actualización masiva de estados de los libros (LibraryBookItem)
            if self.status in ['pending', 'ready']:
                self.items.all().update(status='reserved')
            elif self.status == 'delivered':
                self.items.all().update(status='loaned')
            elif self.status in ['completed', 'canceled']:
                self.items.all().update(status='available')

            # Send email if there was a relevant change
            if status_changed:
                # Use transaction.on_commit to ensure email
                # is sent only if database confirmed the save
                transaction.on_commit(lambda: self.send_notification())
    
    def __str__(self):
        return f"{self.name} ({self.email})"
        
    class Meta:
        verbose_name = _("Reservation")
        verbose_name_plural = _("Reservations")