from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Avg
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.functions import TruncDay, TruncMonth
import json
from calendar import month_name

from .models import Client, Lead, Interaction, Car, Contract
from .forms import ClientForm, LeadForm, InteractionForm, CarForm, ContractForm, CarFilterForm

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


@login_required
def car_list(request):
    """Каталог автомобилей"""
    cars = Car.objects.all()

    # Получение уникальных значений для фильтров
    models = Car.objects.values_list('model_name', flat=True).distinct()
    colors = Car.objects.values_list('color_exterior', flat=True).distinct()
    years = Car.objects.values_list('year_manufacture', flat=True).distinct().order_by('-year_manufacture')

    # Фильтрация
    model_filter = request.GET.get('model')
    status_filter = request.GET.get('status')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    color_filter = request.GET.get('color')
    year_filter = request.GET.get('year')

    if model_filter:
        cars = cars.filter(model_name=model_filter)
    if status_filter:
        cars = cars.filter(status=status_filter)
    if min_price:
        cars = cars.filter(price__gte=min_price)
    if max_price:
        cars = cars.filter(price__lte=max_price)
    if color_filter:
        cars = cars.filter(color_exterior=color_filter)
    if year_filter:
        cars = cars.filter(year_manufacture=year_filter)

    # Статистика
    in_stock_count = Car.objects.filter(status='in_stock').count()
    in_transit_count = Car.objects.filter(status='in_transit').count()
    reserved_count = Car.objects.filter(status='reserved').count()

    # Пагинация
    paginator = Paginator(cars.order_by('-warehouse_arrival_date'), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'cars': page_obj,
        'total_cars': cars.count(),
        'in_stock_count': in_stock_count,
        'in_transit_count': in_transit_count,
        'reserved_count': reserved_count,
        'models': models,
        'colors': colors,
        'years': years,
        'clients': Client.objects.all(),
    }
    return render(request, 'sales/car_list.html', context)


@login_required
def car_detail(request, pk):
    """Детальная информация об автомобиле"""
    car = get_object_or_404(Car, pk=pk)

    # История продаж
    sales_history = Contract.objects.filter(car=car).select_related('client', 'manager')

    context = {
        'car': car,
        'sales_history': sales_history,
        'clients': Client.objects.all(),
        'today': timezone.now().date().isoformat(),
        'max_date': (timezone.now().date() + timezone.timedelta(days=30)).isoformat(),
    }
    return render(request, 'sales/car_detail.html', context)


@login_required
def car_create(request):
    """Создание нового автомобиля"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав для добавления автомобилей')
        return redirect('sales:car_list')

    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save()
            messages.success(request, f'Автомобиль {car.model_name} успешно добавлен')
            return redirect('sales:car_detail', pk=car.pk)
    else:
        form = CarForm()

    context = {
        'form': form,
        'title': 'Добавить автомобиль',
    }
    return render(request, 'sales/car_form.html', context)


@login_required
def car_edit(request, pk):
    """Редактирование автомобиля"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав для редактирования автомобилей')
        return redirect('sales:car_list')

    car = get_object_or_404(Car, pk=pk)

    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            car = form.save()
            messages.success(request, f'Автомобиль {car.model_name} успешно обновлен')
            return redirect('sales:car_detail', pk=car.pk)
    else:
        form = CarForm(instance=car)

    context = {
        'form': form,
        'title': 'Редактировать автомобиль',
    }
    return render(request, 'sales/car_form.html', context)


@login_required
def car_reserve(request, pk):
    """Бронирование автомобиля"""
    if request.method == 'POST':
        car = get_object_or_404(Car, pk=pk)

        if car.status != 'in_stock':
            return JsonResponse({'success': False, 'error': 'Автомобиль не доступен для бронирования'})

        try:
            data = json.loads(request.body)
            client_id = data.get('client_id')
            reserve_until = data.get('reserve_until')

            client = get_object_or_404(Client, pk=client_id)

            # Создаем заявку на бронирование
            lead = Lead.objects.create(
                client=client,
                assigned_manager=request.user,
                source='showroom',
                initial_comment=f'Бронирование автомобиля {car.model_name}',
                status='contract'
            )

            # Меняем статус автомобиля
            car.status = 'reserved'
            car.save()

            return JsonResponse({
                'success': True,
                'lead_id': lead.id,
                'message': 'Автомобиль успешно забронирован'
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def car_delete(request, pk):
    """Удаление автомобиля"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Нет прав'})

    if request.method == 'POST':
        car = get_object_or_404(Car, pk=pk)
        car.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def reports(request):
    """Страница отчетов и аналитики"""

    try:
        # Получение параметров фильтрации
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')

        # Базовые фильтры
        lead_filter = Q(assigned_manager=request.user)
        contract_filter = Q(manager=request.user, signed=True)

        # Применяем фильтры по датам
        if date_from:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            lead_filter &= Q(created_date__date__gte=date_from_obj)
            contract_filter &= Q(contract_date__date__gte=date_from_obj)

        if date_to:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            lead_filter &= Q(created_date__date__lte=date_to_obj)
            contract_filter &= Q(contract_date__date__lte=date_to_obj)

        # Базовая статистика
        total_leads = Lead.objects.filter(lead_filter).count()
        total_sales = Contract.objects.filter(contract_filter).count()

        # Выручка
        revenue_queryset = Contract.objects.filter(contract_filter)
        total_revenue = revenue_queryset.aggregate(total=Sum('final_price'))['total'] or 0

        # Конверсия
        conversion_rate = round((total_sales / total_leads * 100) if total_leads > 0 else 0, 1)

        # Данные для графика (последние 7 дней)
        chart_labels = []
        chart_data = []

        for i in range(6, -1, -1):
            date = timezone.now().date() - timedelta(days=i)
            chart_labels.append(date.strftime('%d.%m'))

            sales_count = Contract.objects.filter(
                contract_filter,
                contract_date__date=date
            ).count()
            chart_data.append(sales_count)

        # Данные для воронки
        funnel_labels = ['Новые', 'В работе', 'Презентация', 'Тест-драйв', 'Оформление', 'Успех', 'Провал']
        funnel_data = []

        status_codes = ['new', 'in_progress', 'presentation', 'test_drive', 'contract', 'success', 'failed']
        for status in status_codes:
            count = Lead.objects.filter(lead_filter, status=status).count()
            funnel_data.append(count)

        # Статистика по источникам
        source_stats = []
        source_labels = []
        source_conversion_data = []

        for source_code, source_name in Client.SOURCE_CHOICES:
            leads_count = Lead.objects.filter(
                lead_filter,
                client__source=source_code
            ).count()

            sales_count = Contract.objects.filter(
                contract_filter,
                client__source=source_code
            ).count()

            conversion = round((sales_count / leads_count * 100) if leads_count > 0 else 0, 1)

            source_stats.append({
                'name': source_name,
                'leads': leads_count,
                'sales': sales_count,
                'conversion': conversion
            })
            source_labels.append(source_name)
            source_conversion_data.append(conversion)

        # Статистика по менеджерам (только текущий пользователь)
        manager_stats = [{
            'id': request.user.id,
            'name': request.user.get_full_name() or request.user.username,
            'sales': total_sales,
            'revenue': total_revenue,
            'avg_check': round(total_revenue / total_sales) if total_sales > 0 else 0
        }]

        # Статистика по автомобилям
        car_stats = Contract.objects.filter(
            contract_filter
        ).values('car__model_name').annotate(
            sales_count=Count('id'),
            revenue=Sum('final_price')
        ).order_by('-sales_count')[:5]

        car_labels = [f'KIA {item["car__model_name"]}' for item in car_stats]
        car_sales_data = [item['sales_count'] for item in car_stats]

        # Список договоров
        contracts = Contract.objects.filter(
            contract_filter
        ).order_by('-contract_date')[:20]

        # Список менеджеров
        from django.contrib.auth.models import User
        managers = User.objects.filter(id=request.user.id)

        context = {
            'total_leads': total_leads,
            'total_sales': total_sales,
            'total_revenue': total_revenue,
            'conversion_rate': conversion_rate,
            'leads_growth': 0,
            'sales_growth': 0,
            'revenue_growth': 0,
            'conversion_growth': 0,
            'chart_labels': json.dumps(chart_labels),
            'chart_data': json.dumps(chart_data),
            'funnel_labels': json.dumps(funnel_labels),
            'funnel_data': json.dumps(funnel_data),
            'source_stats': source_stats,
            'source_labels': json.dumps(source_labels),
            'source_conversion_data': json.dumps(source_conversion_data),
            'manager_stats': manager_stats,
            'manager_labels': json.dumps([manager_stats[0]['name']]) if manager_stats else json.dumps([]),
            'manager_sales_data': json.dumps([manager_stats[0]['sales']]) if manager_stats else json.dumps([]),
            'car_stats': car_stats,
            'car_labels': json.dumps(car_labels),
            'car_sales_data': json.dumps(car_sales_data),
            'plan_sales': 10,
            'plan_completion': round((total_sales / 10 * 100)) if total_sales > 0 else 0,
            'contracts': contracts,
            'date_from': date_from,
            'date_to': date_to,
            'selected_manager': '',
            'managers': managers,
            'next_month': 'Май',
            'forecast_sales': total_sales + 2,
            'forecast_revenue': total_revenue + 1000000,
            'needed_leads': max(5, total_leads),
            'avg_check': round(total_revenue / total_sales) if total_sales > 0 else 3500000,
        }

        return render(request, 'sales/reports.html', context)

    except Exception as e:
        # Если есть ошибка, показываем простую страницу с ошибкой
        return render(request, 'sales/reports.html', {
            'error': str(e),
            'total_leads': 0,
            'total_sales': 0,
            'total_revenue': 0,
            'conversion_rate': 0,
            'chart_labels': json.dumps([]),
            'chart_data': json.dumps([]),
            'funnel_labels': json.dumps([]),
            'funnel_data': json.dumps([]),
            'source_stats': [],
            'source_labels': json.dumps([]),
            'source_conversion_data': json.dumps([]),
            'manager_stats': [],
            'manager_labels': json.dumps([]),
            'manager_sales_data': json.dumps([]),
            'car_stats': [],
            'car_labels': json.dumps([]),
            'car_sales_data': json.dumps([]),
            'plan_sales': 0,
            'plan_completion': 0,
            'contracts': [],
            'date_from': '',
            'date_to': '',
            'selected_manager': '',
            'managers': [],
            'next_month': '',
            'forecast_sales': 0,
            'forecast_revenue': 0,
            'needed_leads': 0,
            'avg_check': 0,
        })