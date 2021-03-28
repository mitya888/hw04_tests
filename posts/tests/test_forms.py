from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        # Создаем пользователя
        cls.user = User.objects.create_user(username='lex')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Описание',
            slug='test-slug'
        )

        cls.post = Post.objects.create(
            text='Текст поста',
            group=cls.group,
            author=cls.user
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), 2)

    def test_edit_post(self):
        """ при редактировании поста через форму на странице
        /<username>/<post_id>/edit/ изменяется
         соответствующая запись в базе данных"""
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        form_data_edit = {
            'text': 'Измененная запись',
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': self.post.author.username,
                'post_id': self.post.id}),
            data=form_data_edit,
            follow=True
        )

        self.assertRedirects(response, reverse('post', kwargs={
            'username': self.post.author.username, 'post_id': self.post.id}))
