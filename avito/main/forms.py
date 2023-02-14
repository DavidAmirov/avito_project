from django import forms

from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from .apps import user_registered
from .models import *

class ChangeUserInfoForm(forms.ModelForm):
    """Форма для изменения личных данных пользователя."""
    email = forms.EmailField(
        required=True,
        label='Адрес электронной почты'
    )
    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'first_name', 'last_name', 'send_message')


class RegisterUserForm(forms.ModelForm):
    """Форма для регистрации поьзователя."""
    email = forms.EmailField(required=True, label='Адрес электронной почты')
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html()
    )
    password2 = forms.CharField(
        label='Пароль(повторно)',
        widget=forms.PasswordInput,
        help_text='Введите пароль повторно'
    )
    
    def clean_password1(self):
        """Метод, валидирующий пароль из значения password1."""
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1
    
    def clean(self):
        """Метод, проверяющий совпадение password1 и password2 """
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors = {'password2':ValidationError(
                'Введенные пароли не совпадают', code='password_mismatch'
            )}
            raise ValidationError(errors)

    def save(self, commit=True):
        """Метод, сохраняющий пользователя, но не делающий его активным.
        После сохранение, подает сигнал на отпраку письма на личную почту
        для активации пользователя."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        user_registered.send(RegisterUserForm, instance=user)
        return user

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2',
                  'first_name', 'last_name', 'send_message')


class SubRubricForm(forms.ModelForm):
    """Форма подрубрики для использования на административном сайте.
    Сделали super_rubric обезательным."""
    super_rubric = forms.ModelChoiceField(
        queryset=SuperRubric.objects.all(),
        empty_label=None, label='Надрубрика',
        required=True
    )
    class Meta:
        model = SubRubric
        fields = '__all__'
