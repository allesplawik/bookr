# Generated by Django 4.2.3 on 2023-07-29 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_publisher'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='publishers',
            field=models.ManyToManyField(to='core.publisher'),
        ),
    ]