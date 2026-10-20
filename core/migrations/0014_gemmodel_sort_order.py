from django.db import migrations, models


def set_initial_gem_order(apps, schema_editor):
    GemModel = apps.get_model("core", "GemModel")
    database = schema_editor.connection.alias
    gems = GemModel.objects.using(database).order_by("-created_at", "id")
    for position, gem in enumerate(gems.iterator()):
        GemModel.objects.using(database).filter(pk=gem.pk).update(sort_order=position)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_chaptermodel_approval_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="gemmodel",
            name="sort_order",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(set_initial_gem_order, migrations.RunPython.noop),
    ]
