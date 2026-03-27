from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .forms import OperatorLoginForm


class OperatorLoginView(LoginView):
    authentication_form = OperatorLoginForm
    redirect_authenticated_user = True
    template_name = 'registration/login.html'


class OperatorLogoutView(LogoutView):
    next_page = 'login'


@login_required
def operator_home(request: HttpRequest) -> HttpResponse:
    return render(request, 'operator/home.html')


login_view = OperatorLoginView.as_view()
logout_view = OperatorLogoutView.as_view()
