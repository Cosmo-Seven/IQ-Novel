from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from decorators.login_decorator import login_required
from helpers.filters import filter_querysets
from decorators.role_decorator import role_permission_required
from core.models import PaymentMethodModel

from constants.message import CREATE, UPDATE, DELETE
from helpers.phone import format_mm_phone


# // Payment Method List -----------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("view_paymentmethodmodel")
def payment_method_list(request):
    payment_methods = PaymentMethodModel.objects.all().order_by("-created_at")

    filters = filter_querysets(
        request,
        payment_methods,
        search_fields=["account_name"],
        date_field="created_at",
        order="-created_at",
    )

    context = {
        "payment_methods": filters["page_obj"],
        **filters,
    }
    return render(request, "dashboard/payment_method_list.html", context)


# // Payment Method Create -----------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("add_paymentmethodmodel")
def payment_method_create(request):
    if request.method == "POST":
        account_name = request.POST.get("account_name")
        logo = request.FILES.get("logo")
        account_number = request.POST.get("account_number")
        account_phone = format_mm_phone(request.POST.get("account_phone"))
        holder_name = request.POST.get("holder_name")

        payment_method = PaymentMethodModel.objects.create(
            account_name=account_name,
            account_phone=account_phone,
            account_number=account_number,
            logo=logo,
            holder_name=holder_name,
        )
        payment_method.save()
        messages.success(request, CREATE)
        return redirect("payment_method_list")


# // Payment Method Update -----------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("change_paymentmethodmodel")
def payment_method_update(request, pk):
    payment_method = get_object_or_404(PaymentMethodModel, id=pk)

    if request.method == "POST":
        payment_method.account_name = request.POST.get("account_name")
        payment_method.account_number = request.POST.get("account_number")
        payment_method.account_phone = format_mm_phone(
            request.POST.get("account_phone")
        )
        payment_method.holder_name = request.POST.get("holder_name")
        if request.FILES.get("logo"):
            if payment_method.logo:
                payment_method.logo.delete(save=False)
            payment_method.logo = request.FILES.get("logo")

        payment_method.save()
        messages.success(request, UPDATE)
        return redirect("payment_method_list")


# // Payment Method Delete -----------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("delete_paymentmethodmodel")
def payment_method_delete(request, pk):
    payment_method = get_object_or_404(PaymentMethodModel, id=pk)
    if request.method == "POST":
        if payment_method.logo:
            payment_method.logo.delete(save=False)
        payment_method.delete()
        messages.success(request, DELETE)
        return redirect("payment_method_list")
