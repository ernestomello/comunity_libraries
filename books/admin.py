from django.contrib import admin

# Register your models here.
from .models import Author, Publisher, Book, Library, LibraryBookItem, Reservation

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
    list_display = ('title', 'get_authors', 'isbn', 'publication_date', 'publisher', 'pages')
    search_fields = ('title', 'isbn')
    list_filter = ('publication_date', 'publisher')

    def get_authors(self, obj):
        return ", ".join([author.name for author in obj.author.all()])
    get_authors.short_description = 'Authors'

@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'city', 'address','email','phone')
    search_fields = ('name', 'city', 'country')
    list_filter = ('country','city')

@admin.register(LibraryBookItem)
class LibraryBookItemAdmin(admin.ModelAdmin):
    list_display = ('book', 'library', 'library__country', 'status')
    search_fields = ('book__title', 'library__name')
    list_filter = ('status',)
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'status', 'status_date')
    fields = ('name', 'email', 'items',  'created_at', 'status','status_date')
    readonly_fields = ('created_at', 'status_date')
    #search_fields = ('user__username', 'book_item__book__title')
    list_filter = ('status', 'created_at', 'status_date')

