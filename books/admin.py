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

admin.site.register(Library)

admin.site.register(LibraryBookItem)
admin.site.register(Reservation)
