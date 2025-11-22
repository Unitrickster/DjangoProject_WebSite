from django import forms
from .models import Client, Lead, Interaction, Car, Contract

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['full_name', 'phone', 'email', 'passport_series', 'passport_number',
                 'passport_issued_by', 'registration_address', 'source']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ФИО'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 XXX XXX-XX-XX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'passport_series': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0000'}),
            'passport_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000000'}),
            'passport_issued_by': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'registration_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'source': forms.Select(attrs={'class': 'form-control'}),
        }

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['client', 'source', 'initial_comment', 'status', 'priority']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'initial_comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
        }

class InteractionForm(forms.ModelForm):
    class Meta:
        model = Interaction
        fields = ['type', 'date_time', 'result', 'next_contact_date']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'result': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Опишите результаты взаимодействия...'}),
            'next_contact_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['vin', 'model_name', 'trim_level', 'color_exterior', 'color_interior',
                 'year_manufacture', 'price', 'status', 'warehouse_arrival_date', 'photo', 'description']
        widgets = {
            'vin': forms.TextInput(attrs={'class': 'form-control'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control'}),
            'trim_level': forms.TextInput(attrs={'class': 'form-control'}),
            'color_exterior': forms.TextInput(attrs={'class': 'form-control'}),
            'color_interior': forms.TextInput(attrs={'class': 'form-control'}),
            'year_manufacture': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'warehouse_arrival_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CarFilterForm(forms.Form):
    model_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Модель автомобиля'
    }))
    status = forms.ChoiceField(
        choices=[('', 'Все статусы')] + Car.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Мин цена',
            'step': '0.01'
        })
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Макс цена',
            'step': '0.01'
        })
    )