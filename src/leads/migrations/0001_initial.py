# Generated by Django 2.1.10 on 2019-08-24 23:11

import core.fields
from django.db import migrations, models
import django.db.models.deletion
import leads.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0005_update_default_language'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeadCode',
            fields=[
                ('id', core.fields.UUIDPrimaryKey(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code_image', models.ImageField(upload_to=leads.models.profile_picture_path)),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='account.Account')),
            ],
        ),
        migrations.CreateModel(
            name='LeadGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True)),
                ('admins', models.ManyToManyField(limit_choices_to={'registration__isnull': False}, related_name='_leadgroup_admins_+', to='account.Account')),
                ('leads', models.ManyToManyField(blank=True, limit_choices_to={'registration__isnull': False}, related_name='_leadgroup_leads_+', to='account.Account')),
            ],
        ),
    ]
