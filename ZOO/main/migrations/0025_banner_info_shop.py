# Generated by Django 4.0.7 on 2022-08-20 12:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_alter_banner_options_remove_banner_background_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='banner',
            name='info_shop',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='banners', to='main.infoshop'),
        ),
    ]
