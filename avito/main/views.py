from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.core.signing import BadSignature
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy


from .models import AdvUser
from .forms import *
from .utilites import signer

def index(request):
    """Функция-контроллер главной страницы"""
    return render(request, 'main/index.html')

def other_page(request, page):
    """Функция-контроллер прочих страниц,
    название шаблона ищется по параметру page"""
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


class AvitoLoginView(LoginView):
    """Класс контроллер авторизации"""
    template_name = 'main/login.html'


class AvitoLogoutView(LoginRequiredMixin, LogoutView):
    """Класс-контроллер выхода с сайта"""
    template_name = 'main/logout.html'


class ChangeUserInfoVIew(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    """Класс-контроллер изменения личных данных.
    В методе setup() добавляем атрибут User_id,
    который понадобится при извлечении объекта."""
    model = AdvUser
    template_name = 'main/change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('main:profile')
    success_message = 'Данные пользователя изменены.'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)
    
    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class AvitoPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    """Класс-контроллер изменения пароля."""
    template_name = 'main/password_change.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Пароль пользователя изменен.'

@login_required
def profile(request):
    """Функция-контроллер для просмотра страницы профиля"""
    return render(request, 'main/profile.html')


class RegisterUserView(CreateView):
    """Класс-контроллер для регистрации нового пользователя."""
    model = AdvUser
    template_name = 'main/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('main:register_done')


class RegisterDoneView(TemplateView):
    """Класс-контроллер успешной регистрациию."""
    template_name = 'main/register_done.html'


def user_activate(request, sign):
    """Фунция-контроллер активации пользователя через письмо."""
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'main/bad_signature.html')
    user = get_object_or_404(AdvUser, username=username)
    if user.is_activated:
        template = 'main/user_is_activated.html'
    else:
        template = 'main/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)


class DeleteUserView(LoginRequiredMixin, DeleteView):
    """Класс-контроллер удаления пользователя.
    В методе setup() добавляем атрибут User_id,
    который понадобится при извлечении объекта.
    В методе post() производится выход пользователя,
    отправка письма об удалении и само удаление."""
    model = AdvUser
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('main:index')

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удален')
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)

def by_rubric(request, pk):
    pass