from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('search/', views.search_books, name='search_books'),
    path('reserve/', views.reserve_books, name='reserve_books'),
    path('altcha/challenge/', views.altcha_challenge, name='altcha_challenge'),
    ]