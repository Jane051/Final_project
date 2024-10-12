# Generated by Django 4.1.1 on 2024-10-09 18:24

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0006_alter_television_categories'),
    ]

    operations = [
        migrations.CreateModel(
            name='MobileConstruction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='MobileDisplay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='MobileOperationSystem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='MobileRAM',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MobileUserMemory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MobilePhone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile_model', models.CharField(max_length=50)),
                ('mobile_released_year', models.IntegerField(validators=[django.core.validators.MinValueValidator(2010), django.core.validators.MaxValueValidator(2024)])),
                ('mobile_screen_size', models.DecimalField(decimal_places=2, max_digits=2)),
                ('smart_phone', models.BooleanField(default=True)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('image', models.ImageField(blank=True, null=True, upload_to='mobile_phone_images/')),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='viewer.brand')),
                ('categories', models.ManyToManyField(blank=True, related_name='mobile_phone', to='viewer.category')),
                ('construction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='viewer.mobileconstruction')),
                ('display', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='viewer.mobiledisplay')),
                ('ram', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='viewer.mobileram')),
                ('user_memory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='viewer.mobileusermemory')),
            ],
        ),
    ]
