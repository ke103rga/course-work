# Generated by Django 5.0.2 on 2024-02-26 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_id', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=200)),
                ('author', models.CharField(max_length=200)),
                ('article_url', models.URLField()),
                ('image_url', models.URLField()),
                ('description', models.CharField(max_length=500)),
                ('published_utc', models.CharField(max_length=12)),
                ('tickers', models.TextField()),
                ('publisher_name', models.CharField(max_length=100)),
            ],
        ),
    ]
