from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_("Tags"))  # Ej: ficción, no ficción, ciencia, historia

    # Campos para sistema de aprobación
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
    assigned_library = models.ForeignKey(
        Library, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name=_("Assigned Library"),
        help_text=_("Library assigned to this user for managing book items")
    )

    def __str__(self):
        return f"{self.user.username} - {self.assigned_library.name if self.assigned_library else 'No library assigned'}"

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crea automáticamente un perfil cuando se crea un usuario
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Guarda el perfil cuando se guarda el usuario
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()

class LibraryBookItem(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE, verbose_name=_("Library"))
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name=_("Book"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Inventary Code"))  # Ej: código de inventario
    STATUS_CHOICES = [
        ('available', _("Available")),
        ('loaned', _("Loaned")),
        ('reserved', _("Reserved")),
        ('lost', _("Lost")),
        # Agrega más estados si lo necesitas
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name=_("Status"))
    
    # Campos de auditoría
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='library_items_created',
        verbose_name=_("Created by")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))

    def clean(self):
        """Validaciones personalizadas"""
        from django.core.exceptions import ValidationError
        
        # Verificar que el libro esté aprobado
        if self.book and not self.book.can_be_used_in_library_items():
            raise ValidationError(_("Only approved books can be added to library inventory"))
        
        # Verificar que el usuario pueda agregar items a esta biblioteca
        if hasattr(self, 'created_by') and self.created_by:
            user_profile = getattr(self.created_by, 'profile', None)
            if user_profile and user_profile.assigned_library and user_profile.assigned_library != self.library:
                raise ValidationError(_("You can only add items to your assigned library"))

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
        ('completed', _("Completed")),
        ('canceled', _("Canceled")),
        ('delivered', _("Delivered")),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Status"))

    def save(self, *args, **kwargs):
        if self.pk:
            orig = Reservation.objects.get(pk=self.pk)
            if orig.status != self.status:
                self.status_date = timezone.now()
        else:
            self.status_date = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.email})"
    class Meta:
        verbose_name = _("Reservation")
        verbose_name_plural = _("Reservations")