# Generated by Django 5.2 on 2025-05-10 23:58

import products.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='original_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(default=0.0, upload_to=products.models.get_upload_path),
            preserve_default=False,
        ),
    ]
