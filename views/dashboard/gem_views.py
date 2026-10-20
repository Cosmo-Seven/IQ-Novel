from core.models import GemModel, GemOrderModel, UserModel
from helpers.filters import filter_querysets
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db import transaction
from django.db.models import Max
from django.http import Http404, HttpResponseNotAllowed
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from decorators.login_decorator import login_required
from decorators.role_decorator import role_permission_required
from constants.message import CREATE, UPDATE, DELETE



# // Gem List ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("view_gemmodel")
def gem_list(request):
    gems = GemModel.objects.all().order_by("sort_order")
    filters = filter_querysets(
        request,
        gems,
        search_fields=[],
        date_field="created_at",
        order="sort_order",
    )
    context = {"gems": filters["page_obj"], **filters}
    return render(request, "dashboard/gem_list.html", context)


@login_required("dashboard_login")
@role_permission_required("change_gemmodel")
def gem_move(request, pk, direction):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    if direction not in {"up", "down"}:
        raise Http404

    with transaction.atomic():
        gems = list(GemModel.objects.select_for_update().order_by("sort_order"))
        index = next((i for i, gem in enumerate(gems) if gem.id == pk), None)
        if index is None:
            raise Http404
        neighbor_index = index - 1 if direction == "up" else index + 1
        if 0 <= neighbor_index < len(gems):
            gem, neighbor = gems[index], gems[neighbor_index]
            gem.sort_order, neighbor.sort_order = neighbor.sort_order, gem.sort_order
            gem.save(update_fields=["sort_order"])
            neighbor.save(update_fields=["sort_order"])

    next_url = request.POST.get("next", "")
    if url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(next_url)
    return redirect(reverse("gem_list"))


# // Gem Order List ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("view_gemordermodel")
def gem_order_list(request):
    orders = GemOrderModel.objects.select_related("user", "gem").order_by("-created_at")
    filters = filter_querysets(
        request,
        orders,
        search_fields=["transaction_id", "user__email", "user__username"],
        date_field="created_at",
        order="-created_at",
    )
    context = {"orders": filters["page_obj"], **filters}
    return render(request, "dashboard/gem_order_list.html", context)


# // Approve Gem Order ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("change_gemordermodel")
def gem_order_approve(request, pk):
    order = get_object_or_404(GemOrderModel, id=pk)
    if request.method == "POST" and order.status != GemOrderModel.STATUS_APPROVED:
        order.status = GemOrderModel.STATUS_APPROVED
        order.approved_by = request.user
        order.save(update_fields=["status", "approved_by"])
        order.user.gem = (order.user.gem or 0) + order.gem_amount
        order.user.save(update_fields=["gem"])
        messages.success(request, "Gem order approved and user balance updated.")
    return redirect("gem_order_list")


# // Reject Gem Order ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("change_gemordermodel")
def gem_order_reject(request, pk):
    order = get_object_or_404(GemOrderModel, id=pk)
    if request.method == "POST" and order.status == GemOrderModel.STATUS_PENDING:
        order.status = GemOrderModel.STATUS_REJECTED
        order.approved_by = request.user
        order.save(update_fields=["status", "approved_by"])
        messages.success(request, "Gem order rejected.")
    return redirect("gem_order_list")


# // Gem Create ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("add_gemmodel")
def gem_create(request):
    if request.method == "POST":
        gem_amount = request.POST.get("gem_amount")
        price = request.POST.get("price")
        is_popular = "is_popular" in request.POST
        sort_order = (GemModel.objects.aggregate(max_order=Max("sort_order"))["max_order"] or 0) + 1
        gem = GemModel.objects.create(
            gem_amount=gem_amount,
            price=price,
            is_popular=is_popular,
            sort_order=sort_order,
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

@login_required("dashboard_login")
def gem_fill_view(request, pk):
    user = get_object_or_404(UserModel, id=pk)
    user.gem = request.POST.get("gem")
    user.save()
    messages.success(request, "Gem fill successfully")
    return redirect("user_list")
