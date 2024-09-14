from django import forms
from .models import Book, Tag, BookTags, Author, Editor, Theme, Type, Cover, Format, Seria
from django.core.exceptions import ValidationError
import re


class TagStringValidator:
    def __call__(self, value):
        if ' ' in value:
            raise ValidationError('Теги не должны содержать пробелов')

class BookForm(forms.ModelForm):

    # в этих блоках можно определять только поля, которые мы хотим кастомизировать
    title = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 1, 'cols': 40}),
        label='Название книги:',
        ##validators=[CodeBlockValidator()]
    )

    author = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        label='Автор книги:',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    editor = forms.ModelChoiceField(
        queryset=Editor.objects.all(),
        label='Издательство:',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    theme  = forms.ModelChoiceField(
        queryset=Theme.objects.all(),
        label='Тематика:',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    type = forms.ModelChoiceField(
        queryset=Type.objects.all(),
        label='Тип книги:',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    cover = forms.ModelChoiceField(
        queryset=Cover.objects.all(),
        label='Тип обложки:',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    format = forms.ModelChoiceField(
        queryset=Format.objects.all(),
        label='Формат книги:',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    seria = forms.ModelChoiceField(
        queryset=Seria.objects.all(),
        label='Серия:',
        empty_label='Серия не выбрана',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    review = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'cols': 40}),
        label='Рецензия на книгу:',
        ##validators=[CodeBlockValidator()]
    )

    file_path = forms.ImageField(
        widget=forms.FileInput(attrs={"id": "image_field"}),
        label='Загрузите файл:',
    )

    tags = forms.CharField(
        label='Теги',
        required=False,
        help_text='Перечислите теги через запятую, без пробелов',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        ##validators=[TagStringValidator()]
    )

    class Meta:
        model = Book  # модель с которой работаем форма
        fields = ['title', 'author', 'tags']  # поля, которые будут в форме и их порядок

        # Виджеты для полей
        widgets =  {
            'title': forms.TextInput(attrs={'class': 'form-control'})
        }

        # Метки для полей
        labels = {
            'title': 'Название книги',
        }

    def clean_tags(self):
        # преобразование строки тегов в список тегов
        tags_str = self.cleaned_data['tags'].lower()
        tag_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        return tag_list

    def save(self, *args, **kwargs):
        instance = super().save(commit=False)
        # Сохраняем карточку в базу данных, чтобы у нее появился id
        # Без id мы не сможем добавить теги
        instance.save()

        current_tags = set(self.cleaned_data['tags'])

        for tag in instance.tags.all():
            if tag.name not in current_tags:
                instance.tags.remove(tag)

        # Обрабатываем теги
        for tag_name in current_tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            # На каждой итерации пополняется таблица много-ко-многим
            instance.tags.add(tag)

        return instance


class UploadFileForm(forms.Form):
    # Здесь определяется поле для загрузки файла
    file = forms.FileField(label='Выберите файл', widget=forms.FileInput(attrs={'class': 'form-control'}))