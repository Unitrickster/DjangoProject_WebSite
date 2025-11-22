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
    path('clients/<int:pk>/', views.client_detail, name='client_detail')
]