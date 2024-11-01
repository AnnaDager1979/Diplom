from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.db.models import F, Q
from django.views.generic import TemplateView, CreateView, ListView
from django.views import View
from django.views.generic.edit import UpdateView
#from social_django.utils import psa

from .forms import (
    CustomAuthenticationForm,
    RegisterUserForm,
    UserPasswordChangeForm,
    ProfileUserForm,
)
from books.models import Book,Favorite
from books.views import MenuMixin

class LoginUser(MenuMixin, LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация'}
    redirect_field_name = 'next'

    def get_success_url(self):
        if self.request.POST.get('next', '').strip():
            return self.request.POST.get('next')
        return reverse_lazy('index')


class LogoutUser(MenuMixin, LogoutView):
    next_page = reverse_lazy('users:login')


class RegisterUser(MenuMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация'}
    success_url = reverse_lazy('users:login')


class RegisterDoneView(MenuMixin, TemplateView):
    template_name = 'users/register_done.html'
    extra_context = {'title': 'Регистрация завершена'}


class ProfileUser(MenuMixin, LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    extra_context = {'title': 'Профиль пользователя', 'active_tab': 'profile'}

    def get_success_url(self):
        # URL на которую будет перенаправлен пользователь после редактирования профиля
        return reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        # Возвращаем объект модели, который должен быть отредактирован
        return self.request.user


class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = 'users/password_change_form.html'
    extra_context = {'title': 'Смена пароля', 'active_tab': 'password_change'}
    success_url = reverse_lazy('users:password_change_done')


class UserPasswordChangeDone(PasswordChangeView):
    template_name = 'users/password_change_done.html'
    extra_context = {'title': 'Смена пароля'}


class UserBooksView(ListView):
    model = Book
    template_name = 'users/profile_books.html'
    context_object_name = 'books'
    extra_context = {'title': 'Мои книги', 'active_tab': 'profile_books'}

    def get_queryset(self):
        queryset = Book.objects.filter(id__in = Favorite.objects.filter(user=self.request.user).values('book'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['favorite_books'] = Book.objects.filter(id__in = Favorite.objects.filter(user=self.request.user).values('book'))
        return context
