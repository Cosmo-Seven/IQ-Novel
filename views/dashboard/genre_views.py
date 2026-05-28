from core.models import GenreModel
from helpers.filters import filter_querysets
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from decorators.login_decorator import login_required
from decorators.role_decorator import role_permission_required
from constants.message import CREATE, UPDATE, DELETE



# // Genre List ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("view_genremodel")
def genre_list(request):
    genres = GenreModel.objects.all().order_by("-created_at")
    filters = filter_querysets(
        request,
        genres,
        search_fields=["name"],
        date_field="created_at",
        order="-created_at",
    )
    context = {"genres": filters["page_obj"], **filters}
    return render(request, "dashboard/genre_list.html", context)


# // Genre Create ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("add_genremodel")
def genre_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        genre = GenreModel.objects.create(
            name=name,
        )
        genre.save()
        messages.success(request, CREATE)
        return redirect("genre_list")


# // Genre Update ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("change_genremodel")
def genre_update(request, pk):
    genre = get_object_or_404(GenreModel, id=pk)
    if request.method == "POST":
        genre.name = request.POST.get("name")
        genre.save()
        messages.success(request, UPDATE)
        return redirect("genre_list")


# // Genre Delete ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("delete_genremodel")
def genre_delete(request, pk):
    genre = get_object_or_404(GenreModel, id=pk)
    genre.delete()
    messages.success(request, DELETE)
    return redirect("genre_list")
