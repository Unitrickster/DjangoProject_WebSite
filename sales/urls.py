from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('leads/', views.lead_list, name='lead_list'),
    path('leads/kanban/', views.lead_kanban, name='lead_kanban'),
    path('clients/', views.client_list, name='client_list'),
    path('cars/', views.car_list, name='car_list'),
    path('reports/', views.reports, name='reports'),
    path('clients/create/', views.client_create, name='client_create'),
    path('clients/<int:pk>/', views.client_detail, name='client_detail'),
path('cars/', views.car_list, name='car_list'),
    path('cars/create/', views.car_create, name='car_create'),
    path('cars/<int:pk>/', views.car_detail, name='car_detail'),
    path('cars/<int:pk>/edit/', views.car_edit, name='car_edit'),
    path('cars/<int:pk>/reserve/', views.car_reserve, name='car_reserve'),
    path('cars/<int:pk>/delete/', views.car_delete, name='car_delete'),
]