"""OnlineShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from viewer.views import BaseView, IndexView, TVDetailView, TVListView, TVCreateView, TVUpdateView, TVDeleteView
from viewer.models import Television, Brand, TVOperationSystem, TVDisplayResolution, TVDisplayTechnology

admin.site.register(Television)
admin.site.register(Brand)
admin.site.register(TVOperationSystem)
admin.site.register(TVDisplayResolution)
admin.site.register(TVDisplayTechnology)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', BaseView.as_view(), name='home'),
    path('index', IndexView.as_view(), name='index'),
    path('tv/list', TVListView.as_view(), name='tv_list'),
    path('tv/create', TVCreateView.as_view(), name='tv_create'),
    path('tv/update/<pk>', TVUpdateView.as_view(), name='tv_update'),
    path('tv/delete/<pk>', TVDeleteView.as_view(), name='tv_delete'),
    path('tv/detail/<pk>', TVDetailView.as_view(), name='tv_detail'),
]
