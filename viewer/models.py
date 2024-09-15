from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime


class Brand(models.Model):
    brand_name = models.CharField(max_length=50)

    def __str__(self):
        return self.brand_name


class TVDisplayTechnology(models.Model):
    name= models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return f'{self.name} - {self.description}'


class TVDisplayResolution(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.name}" ()'


class TVOperationSystem(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Television(models.Model):
    brand_name = models.ForeignKey(Brand, on_delete=models.CASCADE)
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

