# Generated by Django 2.1.11 on 2019-12-17 09:39

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [("feedback", "0018_auto_20191217_1036")]

    operations = [
        migrations.AlterField(
            model_name="registertoken",
            name="token",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, unique=True, verbose_name="Token"
            ),
        )
    ]