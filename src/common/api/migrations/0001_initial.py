# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataAPIRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('request_datetime', models.DateTimeField()),
                ('url', models.CharField(max_length=128, db_index=True)),
                ('module', models.CharField(max_length=64, db_index=True)),
                ('method', models.CharField(max_length=16)),
                ('method_override', models.CharField(max_length=16, null=True)),
                ('query_params', models.TextField()),
                ('response_result', models.BooleanField()),
                ('response_code', models.CharField(max_length=16, db_index=True)),
                ('response_data', models.TextField()),
                ('response_message', models.CharField(max_length=1024, null=True)),
                ('cost_time', models.FloatField()),
                ('request_id', models.CharField(max_length=64, db_index=True)),
            ],
            options={
                'verbose_name': '\u3010\u5e73\u53f0\u65e5\u5fd7\u3011API\u8c03\u7528\u65e5\u5fd7',
                'verbose_name_plural': '\u3010\u5e73\u53f0\u65e5\u5fd7\u3011API\u8c03\u7528\u65e5\u5fd7',
            },
        ),
    ]
