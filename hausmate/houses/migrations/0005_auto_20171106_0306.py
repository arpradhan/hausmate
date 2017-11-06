# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-06 03:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('houses', '0004_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount_paid',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
    ]
