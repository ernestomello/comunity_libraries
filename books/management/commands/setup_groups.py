from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from books.models import Book, LibraryBookItem

class Command(BaseCommand):
    help = 'Setup groups and permissions for the library system'

    def handle(self, *args, **options):
        # Crear el grupo librarian
        librarian_group, created = Group.objects.get_or_create(name='librarian')
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created librarian group')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Librarian group already exists')
            )

        # Obtener los content types
        book_content_type = ContentType.objects.get_for_model(Book)
        library_item_content_type = ContentType.objects.get_for_model(LibraryBookItem)

        # Definir permisos para librarians
        librarian_permissions = [
            # Permisos para libros
            ('add_book', book_content_type),
            ('change_book', book_content_type),
            ('delete_book', book_content_type),
            ('view_book', book_content_type),
            # Permisos para items de biblioteca
            ('add_librarybookitem', library_item_content_type),
            ('change_librarybookitem', library_item_content_type),
            ('delete_librarybookitem', library_item_content_type),
            ('view_librarybookitem', library_item_content_type),
        ]

        # Asignar permisos al grupo librarian
        for perm_codename, content_type in librarian_permissions:
            try:
                permission = Permission.objects.get(
                    codename=perm_codename,
                    content_type=content_type
                )
                librarian_group.permissions.add(permission)
                self.stdout.write(f'Added permission {perm_codename} to librarian group')
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Permission {perm_codename} does not exist')
                )

        # Crear permisos personalizados si no existen
        custom_permissions = [
            ('approve_book', 'Can approve books', book_content_type),
            ('reject_book', 'Can reject books', book_content_type),
        ]

        for codename, name, content_type in custom_permissions:
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                name=name,
                content_type=content_type
            )
            if created:
                self.stdout.write(f'Created custom permission {codename}')
            
            librarian_group.permissions.add(permission)

        self.stdout.write(
            self.style.SUCCESS('Successfully setup groups and permissions')
        )