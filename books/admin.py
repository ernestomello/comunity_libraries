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
    list_display = ('mostrar_portada','title', 'get_authors', 'isbn', 'approval_status', )
    search_fields = ('title', 'isbn')
    list_filter = ('approval_status', 'publication_date', 'publisher', 'created_at')
    filter_horizontal = ('author', 'tags')
    readonly_fields = ('created_by', 'created_at', 'approved_by', 'approved_at')
    
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'author', 'isbn', 'publication_date', 'publisher', 'pages', 'tags','language', 'cover_image', 'description','edition'),
        }),
        ('Approval System', {
            'fields': ('approval_status', 'rejection_reason', 'created_by', 'approved_by', 'approved_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_books', 'reject_books']
    def mostrar_portada(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="width: 50px; height: auto; border-radius: 5px;" />', obj.cover_image.url)
        return "Sin portada"
    
    # This gives the column a title in the Admin
    mostrar_portada.short_description = 'Cover'

    def get_authors(self, obj):
        return ", ".join([author.name for author in obj.author.all()])
    get_authors.short_description = 'Authors'

    def approve_books(self, request, queryset):
        if not request.user.groups.filter(name='librarian').exists():
            messages.error(request, "Only librarians can approve books.")
            return
        
        count = 0
        for book in queryset.filter(approval_status='pending'):
            if book.approve(request.user):
                count += 1
        
        messages.success(request, f"{count} books approved successfully.")
    approve_books.short_description = "Approve selected books"

    def reject_books(self, request, queryset):
        if not request.user.groups.filter(name='librarian').exists():
            messages.error(request, "Only librarians can reject books.")
            return
        
        count = 0
        for book in queryset.filter(approval_status='pending'):
            if book.reject(request.user, "Rejected from admin"):
                count += 1
        
        messages.success(request, f"{count} books rejected.")
    reject_books.short_description = "Reject selected books"
    
    def get_readonly_fields(self, request, obj=None):
        # Fields that only those with special permission can edit
        approval_fields = ('approval_status', 'approved_by', 'rejection_reason')
        
        # If user does NOT have custom permission and is NOT superuser
        if not request.user.has_perm('books.can_approve_book') and not request.user.is_superuser:
            return self.readonly_fields + approval_fields
            
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:  # If it's a new object
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
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        # Filter to libraries assigned to user profile
        if hasattr(request.user, 'profile'):
            user_libraries = request.user.profile.assigned_libraries.all()
            return qs.filter(library__in=user_libraries)
        
        return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "library" and not request.user.is_superuser:
            if hasattr(request.user, 'profile'):
                # Dropdown now shows all libraries assigned to profile
                kwargs["queryset"] = request.user.profile.assigned_libraries.all()
            else:
                kwargs["queryset"] = Library.objects.none()
        
        # Approved books filter (remains the same)
        if db_field.name == "book":
            kwargs["queryset"] = Book.objects.filter(approval_status='approved')
            
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    def save_model(self, request, obj, form, change):
        # If object is new (not an edit), assign creator
        if not change: 
            obj.created_by = request.user
        
        # Call original method to finish saving
        super().save_model(request, obj, form, change)

# UserProfile inline para el admin de User
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('assigned_libraries',)

# Extender el UserAdmin para incluir el profile
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Re-registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user__username', 'user__email',)
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('assigned_libraries',)
    
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'library', 'created_at', 'status', 'status_date', 'show_items_count')
    fields = ('name', 'email', 'library', 'items', 'created_at', 'status', 'status_date')
    readonly_fields = ('created_at', 'status_date', 'library')
    search_fields = ('name', 'email', 'library__name')
    list_filter = ('status', 'created_at', 'status_date', 'library')
    list_editable = ('status',)  # Allow changing status from list without entering the record
    filter_horizontal = ('items',)
    
    def show_items_count(self, obj):
        """Display number of items in the reservation"""
        count = obj.items.count()
        return f"{count} item{'s' if count != 1 else ''}"
    show_items_count.short_description = 'Items'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser and hasattr(request.user, 'profile'):
            return qs.filter(library__in=request.user.profile.assigned_libraries.all())
        return qs

    

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
