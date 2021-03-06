# Generated by Django 2.1.9 on 2019-06-22 10:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0022_auto_20180620_1551'),
        ('sponsors', '0002_auto_20190616_0601'),
    ]

    operations = [
        migrations.CreateModel(
            name='SponsorsListPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='sponsors_sponsorslistplugin', serialize=False, to='cms.CMSPlugin')),
                ('level', models.CharField(choices=[('basic', 'Basic'), ('bronze', 'Bronze'), ('silver', 'Silver'), ('gold', 'Gold'), ('diamond', 'Diamond'), ('tshirt', 'T-Shirt')], max_length=12)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.AddField(
            model_name='sponsor',
            name='level',
            field=models.CharField(choices=[('basic', 'Basic'), ('bronze', 'Bronze'), ('silver', 'Silver'), ('gold', 'Gold'), ('diamond', 'Diamond'), ('tshirt', 'T-Shirt')], default='basic', max_length=12),
        ),
    ]
