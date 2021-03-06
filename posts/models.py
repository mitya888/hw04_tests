from django.db import models
from django.contrib.auth import get_user_model

USER_MODEL = get_user_model()


class Group(models.Model):
    """Создаем модель сообщества с названием Group
    со свойствами:

    Properties
    ----------
    title:
        имя сообщества
    description:
        описание сообщества
    slug :
        уникальный адрес группы"""

    title = models.CharField(
        'Заголовок',
        max_length=200,
        help_text='Дайте название заголовку'
    )
    description = models.TextField(
        'Описание',
        help_text='Придумайте название группы'
    )
    slug = models.SlugField(
        'Ссылка',
        unique=True,
        help_text='Укажите адрес для страницы группы'
    )

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    """метод __str__ нужен для того чтобы при печати
    объекта на экран выводилось поле title"""

    def __str__(self):
        return self.title


class Post(models.Model):
    """Создаем модель сообщества с названием Post
    со свойствами:

    Properties
    ----------
    text:
        текст постов
    pub_date:
        дата публикации постов
    author:
        автор поста
    group:
        принадлежность поста к группе"""

    text = models.TextField(
        "Содержание",
        help_text='Придумай содержание'
    )
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(
        USER_MODEL, on_delete=models.CASCADE, related_name="posts",
        verbose_name="имя"
    )
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="posts", verbose_name="Группа", help_text='Выбери группу'
    )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments')
    author = models.ForeignKey(
        USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments')
    text = models.TextField(
        max_length=100,
        verbose_name='Текст комментария',
        help_text='Добавьте комментарий')
    created = models.DateTimeField('date published', auto_now_add=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.text[0:15]