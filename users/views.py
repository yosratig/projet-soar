from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomLoginForm, UserCreateForm
from .models import CustomUser

def login_view(request):
    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.is_superuser:
                return redirect("users:admin_dashboard")
            elif user.role == "L1":
                return redirect("alerts:l1_dashboard")
            elif user.role == "L2":
                return redirect("alerts:l2_dashboard")
    else:
        form = CustomLoginForm()

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("users:login")


@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect("users:login")

    users = CustomUser.objects.all()
    return render(request, "users/admin_dashboard.html", {"users": users})


@login_required
def create_user(request):
    if not request.user.is_superuser:
        return redirect("users:login")

    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("users:admin_dashboard")
    else:
        form = UserCreateForm()

    return render(request, "users/create_user.html", {"form": form})


@login_required
def delete_user(request, user_id):
    if not request.user.is_superuser:
        return redirect("users:login")

    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    return redirect("users:admin_dashboard")
