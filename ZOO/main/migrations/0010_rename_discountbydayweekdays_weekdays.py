# Generated by Django 4.0.7 on 2022-08-16 12:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_remove_discountbydayweekdays_discount_by_day'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DiscountByDayWeekDays',
            new_name='WeekDays',
        ),
    ]
