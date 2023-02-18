from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.core.signing import BadSignature
from django.core.paginator import Paginator
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Q
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy


from .models import *
from .forms import *
from .utilites import signer

def index(request):
    """Функция-контроллер главной страницы, выводящий последнние 10 объявлений."""
    bbs = Bb.objects.filter(is_active=True)[:10]
    context = {'bbs': bbs}
    return render(request, 'main/index.html', context)

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
    """Функция-контроллер для просмотра страницы профиля пользователя с его объяв."""
    bbs = Bb.objects.filter(author=request.user.pk)
    context = {'bbs': bbs}
    return render(request, 'main/profile.html', context)

@login_required
def profile_bb_detail(request, pk):
    """Функция-контроллер для просмотра определеннгого объявления пользователя."""
    bb = get_object_or_404(Bb, pk=pk)
    ais = bb.additionalimage_set.all()
    context = {'bb': bb, 'ais': ais}
    return render(request, 'main/profile_bb_detail.html', context)


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
    """Функция-контроллер, выводящая объявления по рубрикам.
    В параметре keyword задается поисковое слово.
    страница разделена пагинатором, по 2 объяв. на страницу"""
    rubric = get_object_or_404(SubRubric, pk=pk)
    bbs = Bb.objects.filter(is_active=True, rubric=pk)
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        bbs = bbs.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(bbs, 2)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'rubric': rubric, 'page': page, 'bbs': page.object_list, 'form': form}
    return render(request, 'main/by_rubric.html', context)

def detail(request, rubric_pk, pk):
    """Функиця-контроллер, выводящая отдельно объявление с дополнительной иллюстрацией
    с комментариями"""
    bb = get_object_or_404(Bb, pk=pk)
    ais = bb.additionalimage_set.all()
    comments = Comment.objects.filter(bb=pk, is_active=True)
    initial = {'bb': bb.pk}
    if request.user.is_authenticated:
        initial['author'] = request.user.username
        form_class = UserCommentForm
    else:
        initial['author'] = 'Гость'
        form_class = GuestCommentForm
    form = form_class(initial=initial)
    if request.method =="POST":
        c_form = form_class(request.POST)
        if c_form.is_valid():
            c_form.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Комментарий добавлен')
        else:
            form = c_form
            messages.add_message(request, messages.WARNING,
                                 'Комментарий не добавлен')       
    context = {'bb': bb, 'ais': ais, 'comments': comments, 'form': form}
    return render(request, 'main/detail.html', context)

@login_required
def profile_bb_add(request):
    if request.method == 'POST':
        form = BbForm(request.POST, request.FILES)
        if form.is_valid():
            bb = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=bb)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление добавлено')
                return redirect('main:profile')
    else:
        form = BbForm(initial={'author': request.user.pk})
        formset = AIFormSet()
    context = {'form': form, 'formset': formset}
    return render(request, 'main/profile_bb_add.html', context)

@login_required
def profile_bb_change(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    if request.method =='POST':
        form = BbForm(request.POST, request.FILES, instance=bb)
        if form.is_valid():
            bb = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=bb)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление исправлено')
                return redirect('main:profile')
    else:
        form = BbForm(instance=bb)
        formset = AIFormSet(instance=bb)
    context = {'form': form, 'formset': formset}
    return render(request, 'main/profile_bb_change.html', context)

@login_required
def profile_bb_delete(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    form = BbForm(request.POST, request.FILES, instance=bb)
    if request.method == 'POST':
        bb.delete()
        messages.add_message(request, messages.SUCCESS, 'Удалено')
        return redirect('main:profile')
    else:
        context = {'bb': bb, 'form': form}
        return render(request, 'main/profile_bb_delete.html', context)
