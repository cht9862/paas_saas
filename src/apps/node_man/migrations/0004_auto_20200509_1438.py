# Generated by Django 2.2.8 on 2020-05-09 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('node_man', '0003_auto_20200420_1555'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='node_from',
            field=models.CharField(choices=[('CMDB', 'CMDB'), ('EXCEL', 'EXCEL'), ('NODE_MAN',
                                                                                   'NODE_MAN')], default='NODE_MAN', max_length=45, verbose_name='节点来源'),
        ),
        migrations.AlterField(
            model_name='processstatus',
            name='status',
            field=models.CharField(choices=[('RUNNING', 'RUNNING'), ('UNKNOWN', 'UNKNOWN'), ('TERMINATED', 'TERMINATED'), (
                'NOT_INSTALLED', 'NOT_INSTALLED')], db_index=True, default='UNKNOWN', max_length=45, verbose_name='进程状态'),
        ),
    ]
