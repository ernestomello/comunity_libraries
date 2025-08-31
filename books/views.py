from django.http import JsonResponse
from django.shortcuts import render
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Book, Reservation
from django.db.models import Q

@csrf_exempt
@require_POST
def reserve_books(request):
    data = json.loads(request.body)
    name = data.get('name')
    email = data.get('email')
    isbns = data.get('isbns', [])
    books = Book.objects.filter(isbn__in=isbns)
    if not books.exists():
        return JsonResponse({'message': 'No se encontraron libros para reservar.'}, status=400)
    reservation = Reservation.objects.create(name=name, email=email)
    reservation.books.set(books)
    return JsonResponse({'message': 'Reserva realizada con éxito.'})

def search_books(request):
    query = request.GET.get('q', '')
    books = Book.objects.filter(
        Q(title__icontains=query) | Q(isbn__icontains=query)
    ).select_related('publisher').prefetch_related('author')
    results = []
    for book in books:
        results.append({
            'title': book.title,
            'authors': ', '.join([a.name for a in book.author.all()]),
            'isbn': book.isbn,
            'publisher': book.publisher.name,
        })
    return JsonResponse({'results': results})

def search_page(request):
    return render(request, 'books/search.html')
