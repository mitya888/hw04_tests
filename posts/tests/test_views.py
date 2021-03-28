from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователя
        cls.user = User.objects.create_user(username='gena')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Описание',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user
        )

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_page_names = {
            'index.html': reverse('index'),
            'new_post.html': reverse('new_post'),
            'group.html': reverse('group_posts', kwargs={
                'slug': 'test-slug'}),
            'about/tech.html': reverse('about:tech'),
            'about/author.html': reverse('about:author')
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверка словаря контекста главной страницы
    def test_index_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        post_object = response.context['page'][0]
        post_author_0 = post_object.author
        post_pub_date_0 = post_object.pub_date
        post_text_0 = post_object.text
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_pub_date_0, self.post.pub_date)
        self.assertEqual(post_text_0, self.post.text)

    # Проверка словаря контекста страницы группы
    def test_group_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'test-slug'})
        )
        post_object = response.context['page'][0]
        post_author_0 = post_object.author
        post_pub_date_0 = post_object.pub_date
        post_text_0 = post_object.text

        post_object_group = response.context['group']
        group_title = post_object_group.title
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_pub_date_0, self.post.pub_date)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(group_title, self.group.title)

    # Проверка словаря контекста страницы создания поста
    def test_post_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_index_list_page_list_is_1(self):
        """Удостоверимся, что пост появляется на главной странице сайта"""
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context['page']), 1)

    def test_group_list_page_list_is_1(self):
        """Удостоверимся, что пост появляется на странице выбранной группы"""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'test-slug'}))
        self.assertEqual(len(response.context['page']), 1)

    # Проверка словаря контекста страницы редактирования
    # поста /<username>/<post_id>/edit/
    def test_post_edit_correct_context(self):
        """Шаблон post_new сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            })
        )
        self.assertEqual(response.context['post'], self.post)

    # Проверка словаря контекста страницы профайла пользователя /<username>/
    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.context['page'][0], self.post)
        self.assertEqual(response.context['author'], self.user)

    # Проверка словаря контекста страницы отдельного
    # поста /<username>/<post_id>/
    def test_post_view_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            })
        )
        post_context = {
            'post': self.post,
            'user': self.user
        }
        for key, value in post_context.items():
            with self.subTest(key=key, value=value):
                context = response.context[key]
                self.assertEqual(context, value)
