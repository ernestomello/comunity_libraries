"""
URL configuration for libraries project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.utils.translation import gettext_lazy as _

admin.site.site_url = "https://drive.google.com/drive/folders/1FRfPjx0VQ8jo7fWHyRdGop45oJflX5qe?usp=sharing" #Para agregar el sitio de la ayuda de SGA Administracion
admin.site.site_header = _("C Administración")
admin.site.site_title = _("Inventario Admin Portal")
admin.site.index_title = _("Portal Administrativo ")   
urlpatterns = [
    path('admin/', admin.site.urls),
    path('books/', include('books.urls')),     
]
