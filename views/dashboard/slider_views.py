from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from decorators.login_decorator import login_required
from helpers.filters import filter_querysets
from decorators.role_decorator import role_permission_required
from models.slider_models import SliderModel
from constants.message import CREATE, UPDATE, DELETE


# // Slider List -----------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("view_slidermodel")
def slider_list(request):
    sliders = SliderModel.objects.all().order_by("-created_at")
    filters = filter_querysets(
        request,
        sliders,
        search_fields=[],
        date_field="created_at",
        order="-created_at",
    )
    context = {
        "sliders": filters["page_obj"],
        **filters,
    }
    return render(request, "dashboard/slider_list.html", context)


# // Slider Create -----------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("add_slidermodel")
def slider_create(request):
    if request.method == 'POST':
        slider = SliderModel.objects.create(
            image = request.FILES.get('image'),
        )
        slider.save()
        messages.success(request, CREATE)
        return redirect("slider_list")
    

# // Slider Update -----------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("change_slidermodel")
def slider_update(request,pk):
    slider = SliderModel.objects.get(id=pk)
    if request.method == 'POST':
        if request.FILES.get("image"):
            slider.image.delete()
            slider.image = request.FILES.get('image')
        slider.save()
        messages.success(request, UPDATE)
        return redirect("slider_list")
    

# // Slider Delete -----------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("delete_slidermodel")
def slider_delete(request,pk):
    slider = SliderModel.objects.get(id=pk)
    if slider.image:
        slider.image.delete()
    slider.delete()
    messages.success(request, DELETE)
    return redirect("slider_list")


# // Slider Activate -----------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("delete_slidermodel")
def slider_activate(request,pk):
    slider = SliderModel.objects.get(id=pk)
    slider.status = True
    slider.save()
    messages.success(request, 'Slider activated successfully')
    return redirect("slider_list")


# // Slider Deactivate -----------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("delete_slidermodel")
def slider_deactivate(request,pk):
    slider = SliderModel.objects.get(id=pk)
    slider.status = False
    slider.save()
    messages.success(request, 'Slider deactivated successfully')
    return redirect("slider_list")