# Generated by Django 5.1.3 on 2024-12-01 17:28

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_alter_stocktransaction_performed_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='stocktransaction',
            name='reference_number',
            field=models.CharField(default=uuid.uuid4, editable=False, max_length=36, unique=True),
        ),
        migrations.AddField(
            model_name='stocktransaction',
            name='remarks',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.DeleteModel(
            name='Order',
        ),
    ]