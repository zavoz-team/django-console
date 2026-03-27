from django.contrib.auth.views import LoginView, LogoutView

from .forms import OperatorLoginForm
from .presenters import ui_errors


class OperatorLoginView(LoginView):
    authentication_form = OperatorLoginForm
    redirect_authenticated_user = True
    template_name = 'registration/login.html'

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context = super().get_context_data(**kwargs)
        form = context.get('form')
        if form is not None:
            context['ui_errors'] = ui_errors(form)
        return context


class OperatorLogoutView(LogoutView):
    next_page = 'login'


login_view = OperatorLoginView.as_view()
logout_view = OperatorLogoutView.as_view()
