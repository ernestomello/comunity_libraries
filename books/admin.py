from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib import messages

# Register your models here.
from .models import (
    Author, Publisher, Book, Library, LibraryBookItem, 
    Reservation, Tag, City, Country, UserProfile
)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'birth_date', 'nationality')
    search_fields = ('name',)
    list_filter = ('nationality',)

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'website')
    search_fields = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_authors', 'isbn', 'approval_status', 'created_by', 'created_at', 'approved_by', 'approved_at')
    search_fields = ('title', 'isbn')
    list_filter = ('approval_status', 'publication_date', 'publisher', 'created_at')
    filter_horizontal = ('author', 'tags')
    readonly_fields = ('created_by', 'created_at', 'approved_by', 'approved_at')
    
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'author', 'isbn', 'publication_date', 'publisher', 'pages', 'tags')
        }),
        ('Approval System', {
            'fields': ('approval_status', 'rejection_reason', 'created_by', 'created_at', 'approved_by', 'approved_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_books', 'reject_books']

    def get_authors(self, obj):
        return ", ".join([author.name for author in obj.author.all()])
    get_authors.short_description = 'Authors'

    def approve_books(self, request, queryset):
        if not request.user.groups.filter(name='librarian').exists():
            messages.error(request, "Solo los bibliotecarios pueden aprobar libros.")
            return
        
        count = 0
        for book in queryset.filter(approval_status='pending'):
            if book.approve(request.user):
                count += 1
        
        messages.success(request, f"{count} libros aprobados exitosamente.")
    approve_books.short_description = "Aprobar libros seleccionados"

    def reject_books(self, request, queryset):
        if not request.user.groups.filter(name='librarian').exists():
            messages.error(request, "Solo los bibliotecarios pueden rechazar libros.")
            return
        
        count = 0
        for book in queryset.filter(approval_status='pending'):
            if book.reject(request.user, "Rechazado desde admin"):
                count += 1
        
        messages.success(request, f"{count} libros rechazados.")
    reject_books.short_description = "Rechazar libros seleccionados"

    def save_model(self, request, obj, form, change):
        if not change:  # Si es un objeto nuevo
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'address','email','phone')
    search_fields = ('name', 'city', )
    list_filter = ('city',)

@admin.register(LibraryBookItem)
class LibraryBookItemAdmin(admin.ModelAdmin):
    list_display = ('book', 'library', 'code', 'status', 'created_by', 'created_at')
    search_fields = ('book__title', 'library__name', 'code')
    list_filter = ('status', 'library', 'created_at')
    readonly_fields = ('created_by', 'created_at')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Filtrar solo libros aprobados
        if 'book' in form.base_fields:
            form.base_fields['book'].queryset = Book.objects.filter(approval_status='approved')
        
        # Si el usuario tiene una biblioteca asignada, pre-seleccionarla
        if not obj and hasattr(request.user, 'profile') and request.user.profile.assigned_library:
            form.base_fields['library'].initial = request.user.profile.assigned_library
            
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Si el usuario tiene una biblioteca asignada, mostrar solo items de esa biblioteca
        if hasattr(request.user, 'profile') and request.user.profile.assigned_library:
            if not request.user.is_superuser:
                qs = qs.filter(library=request.user.profile.assigned_library)
        return qs

    def save_model(self, request, obj, form, change):
        if not change:  # Si es un objeto nuevo
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

# UserProfile inline para el admin de User
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('assigned_library',)

# Extender el UserAdmin para incluir el profile
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Re-registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'assigned_library')
    search_fields = ('user__username', 'user__email')
    list_filter = ('assigned_library',)
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'status', 'status_date')
    fields = ('name', 'email', 'items',  'created_at', 'status','status_date')
    readonly_fields = ('created_at', 'status_date')
    #search_fields = ('user__username', 'book_item__book__title')
    list_filter = ('status', 'created_at', 'status_date')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    search_fields = ('name', 'country__name')
    list_filter = ('country',)
