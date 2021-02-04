# Generated by Django 3.1.6 on 2021-02-04 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('wins', models.IntegerField(default=0)),
                ('looses', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('play_date', models.DateTimeField(verbose_name='match datetime')),
                ('finished', models.BooleanField(default=False, verbose_name='finished')),
                ('players', models.ManyToManyField(related_name='matches', to='tournament.Player')),
            ],
        ),
    ]
