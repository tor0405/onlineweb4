# Generated by Django 2.1.11 on 2019-11-17 15:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("feedback", "0014_auto_20191117_1634")]

    operations = [
        migrations.RenameField(
            model_name="multiplechoicerelation",
            old_name="multiple_choice_relation",
            new_name="question",
        )
    ]