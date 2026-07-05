from django.db import migrations

CATEGORIES = [
    ("General Discussion", "general", "Talk about anything and everything.", 0),
    ("Introductions", "introductions", "New here? Say hello.", 1),
    ("Help & Feedback", "help", "Questions, support and site feedback.", 2),
    ("Off-Topic", "off-topic", "Everything that fits nowhere else.", 3),
]


def seed(apps, schema_editor):
    Category = apps.get_model("forum", "Category")
    for name, slug, description, position in CATEGORIES:
        Category.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "description": description, "position": position},
        )


class Migration(migrations.Migration):
    dependencies = [("forum", "0001_initial")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
