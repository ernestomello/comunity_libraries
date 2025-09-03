from django.db import models
from django.utils import timezone

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

class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    author = models.ManyToManyField(Author,verbose_name=_("Author"))
    isbn = models.CharField(max_length=13, unique=True, verbose_name=_("ISBN"))
    publication_date = models.DateField(verbose_name=_("Publication Date"))
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, verbose_name=_("Publisher"))
    pages = models.PositiveIntegerField(verbose_name=_("Number of Pages"))

    def __str__(self):
        return f"{self.title} - {self.author}"
    class Meta:
        verbose_name = _("Book")
        verbose_name_plural = _("Books")
    
class Library(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Library Name"))
    country = models.CharField(max_length=100, verbose_name=_("Country"))
    city = models.CharField(max_length=100, verbose_name=_("City")) 
    address = models.CharField(max_length=255, verbose_name=_("Address"))
    email = models.EmailField(null=True, blank=True, verbose_name=_("Email"))
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name=_("Phone Number"))

    def __str__(self):
        return f"{self.name} ({self.country}/{self.city})"
    class Meta:
        verbose_name = _("Library")
        verbose_name_plural = _("Libraries")

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

    def __str__(self):
        return f"{self.book.title} ({self.code}) en {self.library.name} - {self.get_status_display()}"
    class Meta:
        verbose_name = _("Library Book Item")
        verbose_name_plural = _("Library Book Items")   
    
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