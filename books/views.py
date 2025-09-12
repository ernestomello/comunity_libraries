from django.http import JsonResponse
from django.shortcuts import render
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Reservation, LibraryBookItem, Library
from django.db.models import Q
from django.utils import timezone
import requests

@csrf_exempt
@require_POST
def reserve_books(request):
    recaptcha_response = json.loads(request.body).get('g-recaptcha-response')
    data = {
        'secret': '6LeUcBMlAAAAAF8KX9KX9KX9KX9KX9KX9KX9KX9',
        'response': recaptcha_response
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    result = r.json()
    if not result.get('success'):
        return JsonResponse({'message': 'Captcha inválido. Intenta nuevamente.'}, status=400)
    
    data = json.loads(request.body)
    name = data.get('name')
    email = data.get('email')
    codes = data.get('codes', [])
    items = LibraryBookItem.objects.filter(code__in=codes, status='available')
    if not items.exists():
        return JsonResponse({'message': 'No se encontraron ejemplares disponibles para reservar.'}, status=400)
    reservation = Reservation.objects.create(name=name, email=email)
    reservation.items.set(items)
    # Opcional: cambiar estado de los ejemplares reservados
    items.update(status='reserved')
    return JsonResponse({'message': 'Reserva realizada con éxito.'})

def search_books(request):
    query = request.GET.get('q', '')
    items = LibraryBookItem.objects.filter(
        Q(book__title__icontains=query) | Q(book__isbn__icontains=query)
    ).select_related('book', 'library', 'book__publisher').prefetch_related('book__author')
    results = []
    for item in items:
        results.append({
            'library': item.library.__str__(),
            'address': item.library.address,
            'title': item.book.title,
            'authors': ', '.join([a.name for a in item.book.author.all()]),
            'isbn': item.book.isbn,
            'publisher': item.book.publisher.name,
            'code': item.code,
            'status': item.get_status_display(),
            'is_available': item.status == 'available',
        })
    return JsonResponse({'results': results})

def search_page(request):
    libraries = Library.objects.all()
    return render(request, 'books/search.html', {
        'libraries': libraries,
        'now': timezone.now(),
    })
