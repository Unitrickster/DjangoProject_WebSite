from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class Client(models.Model):
    SOURCE_CHOICES = [
        ('website', '🌐 Сайт'),
        ('phone', '📞 Телефон'),
        ('showroom', '🏢 Шоу-рум'),
        ('recommendation', '👥 Рекомендация'),
    ]

    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    phone = models.CharField(max_length=20, verbose_name='Телефон', unique=True)
    email = models.EmailField(blank=True, verbose_name='Email')
    passport_series = models.CharField(max_length=4, blank=True, verbose_name='Серия паспорта')
    passport_number = models.CharField(max_length=6, blank=True, verbose_name='Номер паспорта')
    passport_issued_by = models.TextField(blank=True, verbose_name='Кем выдан')
    registration_address = models.TextField(blank=True, verbose_name='Адрес регистрации')
    source = models.CharField(max_length=100, choices=SOURCE_CHOICES, verbose_name='Источник')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name

    def get_absolute_url(self):
        return reverse('client_detail', kwargs={'pk': self.pk})


class Car(models.Model):
    STATUS_CHOICES = [
        ('in_stock', '✅ В наличии'),
        ('in_transit', '🚚 В пути'),
        ('reserved', '🔒 Забронирован'),
        ('sold', '💰 Продан'),
    ]

    vin = models.CharField(max_length=17, unique=True, verbose_name='VIN')
    model_name = models.CharField(max_length=100, verbose_name='Модель')
    trim_level = models.CharField(max_length=100, verbose_name='Комплектация')
    color_exterior = models.CharField(max_length=50, verbose_name='Цвет кузова')
    color_interior = models.CharField(max_length=50, blank=True, verbose_name='Цвет салона')
    year_manufacture = models.IntegerField(verbose_name='Год выпуска')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Цена')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_stock')
    warehouse_arrival_date = models.DateField(null=True, blank=True, verbose_name='Дата поступления')
    photo = models.ImageField(upload_to='cars/', blank=True, null=True, verbose_name='Фото')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'
        ordering = ['-warehouse_arrival_date']

    def __str__(self):
        return f"{self.model_name} {self.trim_level} - {self.color_exterior}"


class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', '🆕 Новая'),
        ('in_progress', '🔄 В работе'),
        ('presentation', '📊 Презентация'),
        ('test_drive', '🚗 Тест-драйв'),
        ('contract', '📝 Оформление'),
        ('success', '✅ Успех'),
        ('failed', '❌ Провал'),
    ]

    PRIORITY_CHOICES = [
        (1, '🔴 Высокий'),
        (2, '🟡 Средний'),
        (3, '🟢 Низкий'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')
    assigned_manager = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Менеджер')
    source = models.CharField(max_length=100, verbose_name='Источник заявки')
    initial_comment = models.TextField(blank=True, verbose_name='Комментарий')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2, verbose_name='Приоритет')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_date']

    def __str__(self):
        return f"Заявка #{self.id} - {self.client.full_name}"

    def get_absolute_url(self):
        return reverse('lead_detail', kwargs={'pk': self.pk})


# Добавляем модель Interaction, если она отсутствует
class Interaction(models.Model):
    TYPE_CHOICES = [
        ('call', '📞 Звонок'),
        ('email', '✉️ Email'),
        ('meeting', '👥 Встреча'),
        ('test_drive', '🚗 Тест-драйв'),
        ('note', '📝 Заметка'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Менеджер')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Тип взаимодействия')
    date_time = models.DateTimeField(default=timezone.now, verbose_name='Дата и время')
    result = models.TextField(verbose_name='Результат')
    next_contact_date = models.DateTimeField(null=True, blank=True, verbose_name='Следующий контакт')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Взаимодействие'
        verbose_name_plural = 'Взаимодействия'
        ordering = ['-date_time']

    def __str__(self):
        return f"{self.get_type_display()} с {self.client.full_name}"


class Contract(models.Model):
    PAYMENT_TYPES = [
        ('cash', '💵 Наличные'),
        ('loan', '🏦 Кредит'),
        ('installment', '📅 Рассрочка'),
    ]

    contract_number = models.CharField(max_length=50, unique=True, verbose_name='Номер договора')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Автомобиль')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Менеджер')
    contract_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата заключения')
    final_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Итоговая цена')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, verbose_name='Тип оплаты')
    signed = models.BooleanField(default=False, verbose_name='Подписан')

    class Meta:
        verbose_name = 'Договор'
        verbose_name_plural = 'Договоры'
        ordering = ['-contract_date']

    def __str__(self):
        return f"Договор #{self.contract_number} - {self.client.full_name}"

    def save(self, *args, **kwargs):
        if not self.contract_number:
            last_contract = Contract.objects.order_by('-id').first()
            last_number = int(last_contract.contract_number.split('-')[-1]) if last_contract else 0
            self.contract_number = f"KIA-{timezone.now().year}-{last_number + 1:04d}"
        super().save(*args, **kwargs)