from django.db import migrations, models


def backfill_purchase_mmk(apps, schema_editor):
    ChapterPurchase = apps.get_model("core", "ChapterPurchaseModel")
    GemModel = apps.get_model("core", "GemModel")

    package = (
        GemModel.objects.filter(gem_amount__gt=0)
        .order_by("-is_popular", "-gem_amount")
        .first()
    )
    unit = (
        int(package.price / package.gem_amount)
        if package and package.gem_amount
        else 0
    )

    for purchase in ChapterPurchase.objects.all().iterator():
        sale_price_mmk = int(purchase.gems_paid * unit) if purchase.gems_paid else 0
        percent = purchase.revenue_share_percent or 0
        author_share_mmk = int(sale_price_mmk * percent / 100) if sale_price_mmk else 0
        purchase.sale_price_mmk = sale_price_mmk
        purchase.author_share_mmk = author_share_mmk
        purchase.gem_unit_price_mmk = unit
        purchase.save(
            update_fields=["sale_price_mmk", "author_share_mmk", "gem_unit_price_mmk"]
        )


def backfill_salary_totals(apps, schema_editor):
    AuthorSalary = apps.get_model("core", "AuthorSalaryModel")
    ChapterPurchase = apps.get_model("core", "ChapterPurchaseModel")

    for salary in AuthorSalary.objects.all().iterator():
        purchases = ChapterPurchase.objects.filter(
            chapter__novel__author_id=salary.author_id,
            created_at__year=salary.year,
            created_at__month=salary.month,
        )
        total = sum(p.author_share_mmk for p in purchases)
        salary.total_amount_mmk = total
        salary.save(update_fields=["total_amount_mmk"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="authorsalarymodel",
            old_name="total_gems",
            new_name="total_amount_mmk",
        ),
        migrations.AddField(
            model_name="chapterpurchasemodel",
            name="sale_price_mmk",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="chapterpurchasemodel",
            name="gem_unit_price_mmk",
            field=models.PositiveIntegerField(
                default=0,
                help_text="MMK per gem at time of purchase (for historical records).",
            ),
        ),
        migrations.RenameField(
            model_name="chapterpurchasemodel",
            old_name="author_share_gems",
            new_name="author_share_mmk",
        ),
        migrations.RunPython(backfill_purchase_mmk, migrations.RunPython.noop),
        migrations.RunPython(backfill_salary_totals, migrations.RunPython.noop),
    ]
