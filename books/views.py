from django.http import JsonResponse
from django.shortcuts import render
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Reservation, LibraryBookItem, Library
from django.db.models import Q
from django.utils import timezone
import altcha
from django.conf import settings
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def altcha_challenge(request):
    """Generate an Altcha challenge"""
    # Handle preflight request for CORS
    if request.method == "OPTIONS":
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    
    # Use v1 format for better widget compatibility
    import altcha.v1 as altcha_v1
    
    challenge = altcha_v1.create_challenge(
        algorithm="SHA-256",
        max_number=100000,
        salt_length=12,
        hmac_key=getattr(settings, 'ALTCHA_HMAC_KEY', 'default-secret-key')
    )
    
    response = JsonResponse(challenge.to_dict())
    # Add CORS headers for widget requests
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@csrf_exempt
@require_POST
def reserve_books(request):
    try:
        data = json.loads(request.body)
        altcha_response = data.get('altcha')
        
        # Verify Altcha using v1
        try:
            import altcha.v1 as altcha_v1
            import base64
            
            if not altcha_response:
                return JsonResponse({'message': _('Missing altcha field')}, status=400)
            
            # Try to decode and verify the format
            try:
                decoded_payload = json.loads(base64.b64decode(altcha_response).decode())
            except Exception:
                return JsonResponse({'message': _('Error decoding captcha payload')}, status=400)
            
            # Verify required fields
            required_fields = ['algorithm', 'challenge', 'number', 'salt', 'signature']
            missing_fields = [field for field in required_fields if field not in decoded_payload]
            if missing_fields:
                return JsonResponse({'message': _('Missing required captcha fields')}, status=400)
            
            is_valid, error_msg = altcha_v1.verify_solution(
                altcha_response,
                hmac_key=getattr(settings, 'ALTCHA_HMAC_KEY', 'default-secret-key'),
                check_expires=True
            )
            
            if not is_valid:
                return JsonResponse({'message': _('Invalid captcha. Please try again.')}, status=400)
            
        except Exception:
            return JsonResponse({'message': _('Error verifying captcha')}, status=400)
        
        name = data.get('name')
        email = data.get('email')
        codes = data.get('codes', [])
        
        if not name or not email or not codes:
            return JsonResponse({'message': _('Missing required data (name, email, codes)')}, status=400)
        
        # Obtener elementos disponibles
        items = LibraryBookItem.objects.filter(code__in=codes, status='available').select_related('library')
        if not items.exists():
            return JsonResponse({'message': _('No available items found for reservation.')}, status=400)
        
        # Agrupar elementos por biblioteca
        from itertools import groupby
        from operator import attrgetter
        
        # Ordenar por biblioteca para poder agrupar
        items_by_library = {}
        for item in items:
            library_id = item.library.id
            if library_id not in items_by_library:
                items_by_library[library_id] = {
                    'library': item.library,
                    'items': []
                }
            items_by_library[library_id]['items'].append(item)
        
        # Crear una reserva por cada biblioteca
        reservations_created = []
        for library_data in items_by_library.values():
            library = library_data['library']
            library_items = library_data['items']
            
            # Crear reserva para esta biblioteca (incluir library field)
            reservation = Reservation.objects.create(
                name=name, 
                email=email,
                library=library  # ¡Esta línea faltaba!
            )
            reservation.items.set(library_items)
            
            # Actualizar estado de los elementos
            LibraryBookItem.objects.filter(id__in=[item.id for item in library_items]).update(status='reserved')
            
            reservations_created.append({
                'library_name': library.name,
                'library_address': library.address,
                'items_count': len(library_items),
                'reservation_id': reservation.id
            })
        
        # Preparar mensaje de respuesta
        if len(reservations_created) == 1:
            message = _('Reservation made successfully for %(library)s.') % {'library': reservations_created[0]['library_name']}
        else:
            libraries_list = ', '.join([res['library_name'] for res in reservations_created])
            message = _('%(count)d reservations created successfully for: %(libraries)s.') % {
                'count': len(reservations_created), 
                'libraries': libraries_list
            }
        
        return JsonResponse({
            'message': message,
            'reservations': reservations_created
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'message': _('Invalid JSON data')}, status=400)
    except Exception:
        return JsonResponse({'message': _('Internal server error')}, status=500)

def search_books(request):
    query = request.GET.get('q', '')
    items = LibraryBookItem.objects.filter(
        Q(book__title__icontains=query) | 
        Q(book__isbn__icontains=query) |
        Q(book__author__name__icontains=query) |
        Q(book__publisher__name__icontains=query)
    ).distinct().select_related('book', 'library', 'book__publisher').prefetch_related('book__author')
    results = []
    for item in items:
        # Construir URL de la imagen de portada
        cover_image_url = None
        if item.book.cover_image:
            cover_image_url = item.book.cover_image.url
            
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
            'cover_image_url': cover_image_url,
            'description': item.book.description or '',
            'pages': item.book.pages,
        })
    return JsonResponse({'results': results})

def search_page(request):
    libraries = Library.objects.all()
    return render(request, 'books/search.html', {
        'libraries': libraries,
        'now': timezone.now(),
    })
