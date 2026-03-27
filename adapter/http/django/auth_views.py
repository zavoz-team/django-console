from django.contrib.auth.views import LoginView, LogoutView

from .forms import OperatorLoginForm


class OperatorLoginView(LoginView):
    authentication_form = OperatorLoginForm
    redirect_authenticated_user = True
    template_name = 'registration/login.html'


class OperatorLogoutView(LogoutView):
    next_page = 'login'


login_view = OperatorLoginView.as_view()
logout_view = OperatorLogoutView.as_view()
