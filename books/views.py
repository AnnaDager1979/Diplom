from django.db.transaction import commit
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.db.models import F, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.template.context_processors import request
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import (
    CreateView,
    UpdateView,
    DeleteView
)
from django.views.generic.list import ListView
from django.views import View
from django.contrib.auth.models import User
from django.forms import BaseModelForm

from .forms import BookForm, FavoriteForm, AuthorForm, EditorForm, SeriaForm, UploadFileForm
from .models import Book, Tag, BookTags, Favorite, Author, Editor, Theme, Cover, Type, Format, Seria
import os

info={
   "menu": [
                 {
                     "title": "Главная",
                     "URL":"/",
                     "URL_name":"index",
                  },
                  {
                     "title": "Каталог",
                     "URL":"/books/catalog/",
                     "URL_name": "catalog",
                  },
                  {
                     "title": "Тематический рубрикатор",
                     "URL":"/books/category_list/",
                     "URL_name": "category_list",
                  },
                  {
                     "title": "Серии книг",
                     "URL":"/books/series/",
                     "URL_name": "series",
                  },
                  {
                     "title": "К прочтению",
                     "URL":"/books/reader/",
                     "URL_name": "reader",
                  },
         ],
}

class MenuMixin:

    timeout = 30
    def get_menu(self):
        menu = cache.get('menu')
        if not menu:
            menu = info['menu']
            cache.set('menu', menu, self.timeout)
        return menu

    def get_books_count(self):
        books_count = cache.get('books_count')
        if not books_count:
            books_count = Book.objects.count()
            cache.set('books_count', books_count, self.timeout)
        return books_count

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = self.get_menu()
        context['books_count'] = self.get_books_count()
        return context

class IndexView(MenuMixin, TemplateView):
    template_name = "main.html"

class PageNotFoundView(MenuMixin, TemplateView):
    template_name = "404.html"

class CatalogView(MenuMixin, ListView):
    model = Book
    template_name = 'books/catalog.html'
    context_object_name = 'books'
    paginate_by = 6

    def get_queryset(self):
        sort = self.request.GET.get('sort', 'title')
        order = self.request.GET.get('order', 'asc')
        search_query = self.request.GET.get('search_query', '')

        if order == 'asc':
            order_by = sort
        else:
            order_by = f'-{sort}'

        if search_query:
            queryset = Book.objects.filter(
                Q(title__iregex=search_query) |
                Q(author__sirname__iregex=search_query) |
                Q(tags__name__iregex=search_query)
            ).prefetch_related('tags').order_by(order_by).distinct()
        else:
            queryset = Book.objects.prefetch_related('tags').order_by(order_by)
        return queryset

    def get_context_data(self, **kwargs):
        # Получение существующего контекста из базового класса
        context = super().get_context_data(**kwargs)
        # Добавление дополнительных данных в контекст
        context['sort'] = self.request.GET.get('sort', 'title')
        context['order'] = self.request.GET.get('order', 'asc')
        context['search_query'] = self.request.GET.get('search_query', '')
        context['menu'] = info['menu'] # Пример добавления статических данных в контекст
        try:
            if self.request.user:
                context['favorite_books'] = Book.objects.filter(id__in = Favorite.objects.filter(user=self.request.user).values('book'))
        except:
            0
        return context


class BookByThemeListView(MenuMixin, ListView):
    model = Book
    template_name = 'books/catalog.html'
    context_object_name = 'books'
    paginate_by = 30

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        theme = get_object_or_404(Theme, slug=slug)

        return Book.objects.filter(theme=theme)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['theme'] = get_object_or_404(Theme, slug=self.kwargs.get('slug'))
        return context


def get_books_by_tag(request, tag_id):

    books = Book.objects.filter(tags__id=tag_id)

    context = {
        'books': books,
        'menu': info['menu'],
    }
    return render(request, 'books/catalog.html', context)

class BookDetailView(MenuMixin, DetailView):
    model = Book  # Указываем, что моделью для этого представления является Card
    template_name = 'books/book_detail.html'  # Указываем путь к шаблону для детального отображения карточки
    context_object_name = 'book'  # Переопределяем имя переменной в контексте шаблона

    # Метод для обновления счетчика просмотров при каждом отображении детальной страницы карточки
    def get_object(self, queryset=None):
        # Получаем объект с учетом переданных в URL параметров (в данном случае, pk или id карточки)
        obj = super().get_object(queryset=queryset)
        return obj


class SeriaView(MenuMixin, ListView):
    model = Seria  # Указываем модель, данные которой мы хотим отобразить
    template_name = 'books/series.html'  # Путь к шаблону, который будет использоваться для отображения страницы
    context_object_name = 'series'

    def get_queryset(self):
        # Получение параметров сортировки из GET-запроса
        sort = self.request.GET.get('sort', 'seria')
        order = self.request.GET.get('order', 'asc')
        search_query = self.request.GET.get('search_query', '')

        # Определение направления сортировки
        if order == 'asc':
            order_by = sort
        else:
            order_by = f'-{sort}'

        # Фильтрация карточек по поисковому запросу и сортировка
        if search_query:
            queryset = Seria.objects.filter(seria__iregex=search_query).order_by(order_by)
        else:
            queryset = Seria.objects.order_by(order_by)
        return queryset

    def get_context_data(self, **kwargs):
        # Получение существующего контекста из базового класса
        context = super().get_context_data(**kwargs)
        # Добавление дополнительных данных в контекст
        context['sort'] = self.request.GET.get('sort', 'seria')
        context['order'] = self.request.GET.get('order', 'asc')
        context['search_query'] = self.request.GET.get('search_query', '')
        # Добавление статических данных в контекст, если это необходимо
        context['menu'] = info['menu'] # Пример добавления статических данных в контекст
        context['books'] = Book.objects.all()
        return context


class GetControl(ListView):
    model = Book
    template_name = 'books/to_read.html'
    context_object_name = 'books'

    def get_queryset(self):
        queryset = Book.objects.filter(controler=1)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = Book.objects.filter(controler=1)
        context['favorite_books'] = Book.objects.filter(controler=1).filter(id__in=Favorite.objects.filter(user=self.request.user).values('book'))
        context['menu'] = info['menu']
        return context


class CategoryListView(MenuMixin, ListView):
    model = Theme
    template_name = "books/category_list.html"


class BookByCategoryView(MenuMixin, ListView):
    model = Theme
    context_object_name = 'books'
    template_name = 'books/book_list.html'

    def get_queryset(self):
        self.title = Theme.objects.get(slug=self.kwargs['slug'])
        queryset = Book.objects.filter(theme=self.title)
        self.parent = Theme.objects.get(slug=self.kwargs['slug'])

        theme_list=[] ##Выбираем все тематики связанные с выбранной
        parent_list = []

        for theme in Theme.objects.all():
             if theme.parent==self.parent:
                theme_list.append(theme.title)
                parent_list.append(Theme.objects.get(title = theme.title))
                for book in Book.objects.filter(theme=theme):
                    queryset |= Book.objects.filter(id=book.id)

        for theme in Theme.objects.all():
            if theme.parent in parent_list:
                theme_list.append(theme.title)
                parent_list.append(Theme.objects.get(title=theme.title))
                for book in Book.objects.filter(theme=theme):
                    queryset |= Book.objects.filter(id=book.id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        menu: info['menu']
        context['themes'] = Theme.objects.all()
        return context

def handle_uploaded_file(f):
        file_path = f'books/static/books/images/{f.name}'

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb+") as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        return file_path

def add_book_by_file(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('catalog')
    else:
        form = BookForm
    return render(request, 'books/add_book.html', {'form':form})


class AddBookCreateView(MenuMixin, CreateView):
    model = Book
    form_class = BookForm
    extra_context = {'books': Book.objects.all()}
    template_name = 'books/add_book.html'
    success_url = reverse_lazy('catalog')
    redirect_field_name = 'next'


class AddAuthorCreateView(MenuMixin, CreateView):
    model = Author
    form_class = AuthorForm
    template_name = 'books/add_author.html'
    success_url = reverse_lazy('add_book')
    redirect_field_name = 'next'

class AddEditorCreateView(MenuMixin, CreateView):
    model = Editor
    form_class = EditorForm
    template_name = 'books/add_editor.html'
    success_url = reverse_lazy('add_book')
    redirect_field_name = 'next'

class AddSeriaCreateView(MenuMixin, CreateView):
    model = Seria
    form_class = SeriaForm
    template_name = 'books/add_seria.html'
    success_url = reverse_lazy('add_book')
    redirect_field_name = 'next'

class EditBookUpdateView(LoginRequiredMixin, MenuMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'books/add_book.html'
    success_url = reverse_lazy('catalog')
    redirect_field_name = 'next'

class DeleteBookView(LoginRequiredMixin, MenuMixin, DeleteView):
    model = Book  # Указываем модель, с которой работает представление
    success_url = reverse_lazy('catalog')  # URL для перенаправления после успешного удаления карточки
    template_name = 'books/delete_book.html'  # Указываем шаблон, который будет использоваться для отображения формы подтверждения удаления
    redirect_field_name = 'next'  # Имя параметра URL, используемого для перенаправления после успешного входа в систему

class AddFavoriteBookCreateView(MenuMixin, CreateView, ListView):
    model = Favorite
    form_class = FavoriteForm
    template_name = 'books/add_favorite.html'
    context_object_name = 'books'
    success_url = reverse_lazy('catalog')
    redirect_field_name = 'next'

    def get_queryset(self):
        self.id = Book.objects.get(id=self.kwargs['book_id']).id
        queryset = Book.objects.filter(id=self.id)
        return queryset

    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['menu'] = info['menu'] # Пример добавления статических данных в контекст
       context['bookid'] = Book.objects.get(id=self.kwargs['book_id']).id
       context['book'] = Book.objects.all()
       return context

    def get_initial(self):
        return {'user': self.request.user}


class DeleteFavoriteBookView(MenuMixin, ListView):
    model = Favorite  # Указываем модель, с которой работает представление
    success_url = reverse_lazy('catalog')  # URL для перенаправления после успешного удаления карточки
    template_name = 'books/delete_favorite.html'  # Указываем шаблон, который будет использоваться для отображения формы подтверждения удаления
    redirect_field_name = 'next'  # Имя параметр

    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       book = Book.objects.get(id=self.kwargs['book'])
       message = "Книга удалена из избранного"
       favorite_book=Favorite.objects.filter(book=book.id).filter(user=self.request.user)
       favorite_book.delete()
       context['message'] = message
       return context

