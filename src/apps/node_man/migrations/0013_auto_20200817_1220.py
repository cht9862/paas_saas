# Generated by Django 2.2.8 on 2020-08-17 04:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("node_man", "0012_subscription_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="subscription", name="is_main", field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name="processstatus",
            name="status",
            field=models.CharField(
                choices=[
                    ("RUNNING", "RUNNING"),
                    ("UNKNOWN", "UNKNOWN"),
                    ("TERMINATED", "TERMINATED"),
                    ("NOT_INSTALLED", "NOT_INSTALLED"),
                    ("UNREGISTER", "UNREGISTER"),
                ],
                db_index=True,
                default="UNKNOWN",
                max_length=45,
                verbose_name="进程状态",
            ),
        ),
    ]
