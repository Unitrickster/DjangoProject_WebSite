from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Client, Lead, Car
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Client, Lead, Interaction, Contract
from . forms import ClientForm, InteractionForm
@login_required
def dashboard(request):
    context = {
        'total_clients': Client.objects.count(),
        'total_leads': Lead.objects.filter(assigned_manager=request.user).count(),
        'total_cars': Car.objects.count(),
        'active_leads': Lead.objects.filter(assigned_manager=request.user, status='new').count(),
    }
    return render(request, 'sales/dashboard.html', context)

@login_required
def lead_list(request):
    leads = Lead.objects.filter(assigned_manager=request.user)
    return render(request, 'sales/lead_list.html', {'leads': leads})

@login_required
def lead_kanban(request):
    leads_by_status = {}
    for status_code, status_name in Lead.STATUS_CHOICES:
        leads = Lead.objects.filter(assigned_manager=request.user, status=status_code)
        leads_by_status[status_code] = {
            'name': status_name,
            'leads': leads
        }
    return render(request, 'sales/lead_kanban.html', {'leads_by_status': leads_by_status})

@login_required
def client_list(request):
    clients = Client.objects.all()
    return render(request, 'sales/client_list.html', {'clients': clients})

@login_required
def car_list(request):
    cars = Car.objects.all()
    return render(request, 'sales/car_list.html', {'cars': cars})

@login_required
def reports(request):
    return render(request, 'sales/reports.html')


def update_lead_status(request, pk):
    """Обновление статуса заявки через AJAX"""
    if request.method == 'POST':
        lead = get_object_or_404(Lead, pk=pk, assigned_manager=request.user)
        new_status = request.POST.get('status')

        if new_status in dict(Lead.STATUS_CHOICES):
            lead.status = new_status
            lead.save()

            return JsonResponse({
                'success': True,
                'new_status': lead.get_status_display()
            })

    return JsonResponse({'success': False}, status=400)


@login_required
def client_list(request):
    """Список клиентов"""
    clients_list = Client.objects.all().order_by('-created_at')

    # Пагинация
    paginator = Paginator(clients_list, 25)
    page_number = request.GET.get('page')
    clients = paginator.get_page(page_number)

    context = {
        'clients': clients,
    }
    return render(request, 'sales/client_list.html', context)


@login_required
def client_detail(request, pk):
    """Детальная информация о клиенте"""
    client = get_object_or_404(Client, pk=pk)
    interactions = Interaction.objects.filter(client=client).order_by('-date_time')
    leads = Lead.objects.filter(client=client).select_related('assigned_manager')
    contracts = Contract.objects.filter(client=client).select_related('car')

    if request.method == 'POST':
        form = InteractionForm(request.POST)
        if form.is_valid():
            interaction = form.save(commit=False)
            interaction.client = client
            interaction.manager = request.user
            interaction.save()
            messages.success(request, 'Взаимодействие успешно добавлено')
            return redirect('client_detail', pk=client.pk)
    else:
        form = InteractionForm(initial={'client': client})

    context = {
        'client': client,
        'interactions': interactions,
        'leads': leads,
        'contracts': contracts,
        'form': form,
    }
    return render(request, 'sales/client_detail.html', context)


@login_required
def client_create(request):
    """Создание нового клиента"""
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, f'Клиент {client.full_name} успешно создан')
            return redirect('client_detail', pk=client.pk)
    else:
        form = ClientForm()

    context = {
        'form': form,
        'title': 'Добавить клиента'
    }
    return render(request, 'sales/client_form.html', context)