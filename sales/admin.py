from django.contrib import admin
from .models import Client, Car, Lead

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'email', 'source', 'created_at']
    list_filter = ['source', 'created_at']
    search_fields = ['full_name', 'phone']

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'trim_level', 'color_exterior', 'price', 'status']
    list_filter = ['status', 'model_name']
    search_fields = ['vin', 'model_name']

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'assigned_manager', 'status', 'created_date']
    list_filter = ['status', 'created_date', 'assigned_manager']