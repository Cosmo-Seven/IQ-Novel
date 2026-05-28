from core.models import GemModel
from helpers.filters import filter_querysets
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from decorators.login_decorator import login_required
from decorators.role_decorator import role_permission_required
from constants.message import CREATE, UPDATE, DELETE



# // Gem List ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("view_gemmodel")
def gem_list(request):
    gems = GemModel.objects.all().order_by("-created_at")
    filters = filter_querysets(
        request,
        gems,
        search_fields=[],
        date_field="created_at",
        order="-created_at",
    )
    context = {"gems": filters["page_obj"], **filters}
    return render(request, "dashboard/gem_list.html", context)


# // Gem Create ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("add_gemmodel")
def gem_create(request):
    if request.method == "POST":
        gem_amount = request.POST.get("gem_amount")
        price = request.POST.get("price")
        is_popular = "is_popular" in request.POST
        gem = GemModel.objects.create(
            gem_amount=gem_amount,
            price=price,
            is_popular=is_popular,
        )
        gem.save()
        messages.success(request, CREATE)
        return redirect("gem_list")


# // Gem Update ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("change_gemmodel")
def gem_update(request, pk):
    gem = get_object_or_404(GemModel, id=pk)
    if request.method == "POST":
        gem.gem_amount = request.POST.get("gem_amount")
        gem.price = request.POST.get("price")
        gem.is_popular = "is_popular" in request.POST
        gem.save()
        messages.success(request, UPDATE)
        return redirect("gem_list")


# // Gem Delete ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("delete_gemmodel")
def gem_delete(request, pk):
    gem = get_object_or_404(GemModel, id=pk)
    gem.delete()
    messages.success(request, DELETE)
    return redirect("gem_list")
