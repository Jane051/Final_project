from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, RegexValidator
import datetime
import uuid


class Brand(models.Model):
    brand_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.brand_name


class TVDisplayTechnology(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class TVDisplayResolution(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class TVOperationSystem(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Television(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    brand_model = models.CharField(max_length=50)
    tv_released_year = models.IntegerField(validators=[
            MinValueValidator(2010),
            MaxValueValidator(datetime.date.today().year)
        ])
    tv_screen_size = models.IntegerField()
    smart_tv = models.BooleanField(default=True)
    refresh_rate = models.IntegerField()
    display_technology = models.ForeignKey(TVDisplayTechnology, on_delete=models.CASCADE)
    display_resolution = models.ForeignKey(TVDisplayResolution, on_delete=models.CASCADE)
    operation_system = models.ForeignKey(TVOperationSystem, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    categories = models.ManyToManyField(Category, related_name="televisions", blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.00)
    image = models.ImageField(upload_to='television_images/', blank=True, null=True)

    def __str__(self):
        return f'{self.brand} -  {self.brand_model} - {self.tv_screen_size}"'


class MobileOperationSystem(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class MobileRAM(models.Model):
    size = models.IntegerField(null=True, blank=True, unique=True)

    def __str__(self):
        return f"{self.size} GB"


class MobileUserMemory(models.Model):
    size = models.IntegerField(null=True, blank=True, unique=True)

    def __str__(self):
        return f"{self.size} GB"


class MobileConstruction(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class MobileDisplay(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class MobilePhone(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    mobile_model = models.CharField(max_length=50)
    mobile_released_year = models.IntegerField(validators=[
        MinValueValidator(2010),
        MaxValueValidator(datetime.date.today().year)
    ])
    mobile_screen_size = models.DecimalField(max_digits=2, decimal_places=2)
    smart_phone = models.BooleanField(default=True)
    ram = models.ForeignKey(MobileRAM, on_delete=models.CASCADE)
    user_memory = models.ForeignKey(MobileUserMemory, on_delete=models.CASCADE)
    construction = models.ForeignKey(MobileConstruction, on_delete=models.CASCADE)
    display = models.ForeignKey(MobileDisplay, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    categories = models.ManyToManyField(Category, related_name="mobile_phone", blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.00)
    image = models.ImageField(upload_to='mobile_phone_images/', blank=True, null=True)

    def __str__(self):
        return f'{self.brand} -  {self.mobile_model}'


class Profile(models.Model):
    ROLE_CHOICES = [
        ('ADMINISTRATOR', 'Administrator'),
        ('USER', 'User'),
    ]

    COMMUNICATION_CHANNEL_CHOICES = [
        ('POST', 'Pošta'),
        ('EMAIL', 'Email'),
        ('TELEPHONE', 'Telefon'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(null=True, max_length=50)
    last_name = models.CharField(null=True, max_length=50)
    phone_number = models.CharField(
        max_length=14,
        validators=[
            RegexValidator(regex='^\+?\d+$', message='Nesprávný formát čísla.'),
            MinLengthValidator(9, message='Telefonní číslo musí mít alespoň 9 znaků.')
        ],
        blank=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=25, blank=True)
    zipcode = models.CharField(max_length=5, blank=True)
    avatar = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='USER')
    communication_channel = models.CharField(max_length=10, choices=COMMUNICATION_CHANNEL_CHOICES, default='EMAIL')

    @property
    def email(self):
        return self.user.email

    def __str__(self):
        return f'{self.user.username} Profile'


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('pending_payment', 'Pending Payment'),
        ('processing', 'Processing'),
        ('on_hold', 'On Hold'),
        ('dispatched', 'Dispatched'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('returned', 'Returned'),
        ('completed', 'Completed'),
    ]

    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders')
    television = models.ManyToManyField(Television)
    mobile_phone = models.ManyToManyField(MobilePhone)
    order_date = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    zipcode = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='submitted')

    def __str__(self):
        return f"Order #{self.order_id} by {self.user}"
