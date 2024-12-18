# Generated by Django 4.2.4 on 2024-12-16 18:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("employee", "0001_initial"),
        ("project", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Allocation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("allocation_percentage", models.FloatField()),
                ("allocation_start_date", models.DateField()),
                ("allocation_end_date", models.DateField()),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="employee.employee",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="project.project",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["employee", "project"],
                        name="allocation__employe_f00169_idx",
                    ),
                    models.Index(
                        fields=["allocation_start_date", "allocation_end_date"],
                        name="allocation__allocat_488e44_idx",
                    ),
                ],
            },
        ),
    ]
