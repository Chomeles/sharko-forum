from django.db import migrations

# slug -> (name, section, icon, description, position)
NODES = {
    "announcements": ("Announcements", "Community", "📢", "News and site updates.", 0),
    "general": ("General Discussion", "Community", "💬", "Talk about anything and everything.", 1),
    "introductions": ("Introductions", "Community", "👋", "New here? Say hello.", 2),
    "off-topic": ("Off-Topic", "Community", "🎲", "Everything that fits nowhere else.", 3),
    "help": ("Help & Feedback", "Support", "🛠️", "Questions, support and site feedback.", 0),
}


def seed(apps, schema_editor):
    Category = apps.get_model("forum", "Category")
    for slug, (name, section, icon, description, position) in NODES.items():
        Category.objects.update_or_create(
            slug=slug,
            defaults={
                "name": name,
                "section": section,
                "icon": icon,
                "description": description,
                "position": position,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("forum", "0003_alter_category_options_category_icon_and_more")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
