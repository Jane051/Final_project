from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime


class Brand(models.Model):
    brand_name = models.CharField(max_length=50)

    def __str__(self):
        return self.brand_name


class TVDisplayTechnology(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class TVDisplayResolution(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class TVOperationSystem(models.Model):
    name = models.CharField(max_length=50)

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
    categories = models.ManyToManyField(Category, related_name="televisions")

    def __str__(self):
        return f'{self.brand_name} -  {self.brand_model} - {self.tv_screen_size}"'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    biography = models.TextField()

    @property
    def email(self):
        return self.user.email
