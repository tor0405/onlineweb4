# Generated by Django 2.2.11 on 2020-03-28 09:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("approval", "0010_auto_20200321_1924")]

    operations = [
        migrations.AlterField(
            model_name="committeeapplication",
            name="committees",
            field=models.ManyToManyField(
                through="approval.CommitteePriority",
                to="authentication.OnlineGroup",
                verbose_name="komiteer",
            ),
        ),
        migrations.AlterField(
            model_name="committeepriority",
            name="group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="authentication.OnlineGroup",
                verbose_name="komite",
            ),
        ),
    ]