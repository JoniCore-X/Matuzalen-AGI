"""autodjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.views.generic import TemplateView
from cognitive_api.views import api_root

urlpatterns = [
    path('', TemplateView.as_view(template_name='chat.html'), name='chat_ui'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login_ui'),
    path('api-info/', api_root, name='api_root'),
    path('admin/', admin.site.urls),
    path('api/', include('cognitive_api.urls')),
]
