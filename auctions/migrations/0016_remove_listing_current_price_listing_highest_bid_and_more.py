# Generated by Django 4.0.4 on 2022-06-02 17:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0015_alter_user_watchlist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='current_price',
        ),
        migrations.AddField(
            model_name='listing',
            name='highest_bid',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='auctions.bid'),
        ),
        migrations.AddField(
            model_name='listing',
            name='start_price',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=6),
        ),
    ]