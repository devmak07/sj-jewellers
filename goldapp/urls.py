from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('download_merchants_pdf/', views.download_merchants_pdf, name='download_merchants_pdf'),
]