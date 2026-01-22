from django.db import migrations, models


def map_age_bands(apps, schema_editor):
    FoundingFamilySignup = apps.get_model("founding", "FoundingFamilySignup")
    mappings = {
        "6-8": "IMAGINAUTS",
        "9-11": "NAVIGATORS",
        "12-14": "NAVIGATORS",
        "15-16": "TRAILBLAZERS",
    }
    for old_value, new_value in mappings.items():
        FoundingFamilySignup.objects.filter(child_age_range=old_value).update(
            child_age_range=new_value
        )


class Migration(migrations.Migration):
    dependencies = [
        ("founding", "0001_initial"),
    ]

    operations = [
        # First, increase the max_length to accommodate the new values
        migrations.AlterField(
            model_name="foundingfamilysignup",
            name="child_age_range",
            field=models.CharField(
                choices=[
                    ("IMAGINAUTS", "Imaginauts (6–10)"),
                    ("NAVIGATORS", "Navigators (11–13)"),
                    ("TRAILBLAZERS", "Trailblazers (14–16)"),
                ],
                max_length=16,
            ),
        ),
        # Then, update the existing data
        migrations.RunPython(map_age_bands, migrations.RunPython.noop),
    ]
