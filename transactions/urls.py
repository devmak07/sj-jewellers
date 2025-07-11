from django.urls import path
from . import views

urlpatterns = [
    path("", views.transactions_tabs, name="transactions_tabs"),
    path("edit/<int:pk>/", views.edit_transaction, name="edit_transaction"),
    path("delete/<int:pk>/", views.delete_transaction, name="delete_transaction"),
    path("toggle_status/<int:pk>/", views.toggle_status, name="toggle_status"),
    path("mark_paid/<int:pk>/", views.mark_paid, name="mark_paid"),
    path('calculation/', views.calculation, name='calculation'),
    path('calculation/pdf/', views.calculation_pdf, name='calculation_pdf'),
    path('calculation/history/', views.calculation_history, name='calculation_history'),
    path('calculation/history/pdf/', views.calculation_history_pdf, name='calculation_history_pdf'),
    path('calculation/delete/<int:pk>/', views.delete_calculation_history, name='delete_calculation_history'),
]
