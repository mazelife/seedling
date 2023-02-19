from django.db import migrations, models


class Migration(migrations.Migration):
    """Add a column called "anomalous"""

    dependencies = [
        ("climate", "0001_add_climate_reading"),
    ]

    operations = [
        migrations.AddField(
            model_name="climatereading",
            name="anomalous",
            field=models.BooleanField(default=False),
        ),
    ]
