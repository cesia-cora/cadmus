# Generated by Django 4.1.1 on 2022-11-21 20:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cadmus', '0005_alter_entry_creator_alter_entry_initial_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]