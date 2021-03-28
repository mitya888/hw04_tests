from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from posts.models import Group, Post


User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_homepage(self):
        # Делаем запрос к главной странице и проверяем статус
        response = self.guest_client.get('/')
        # Утверждаем, что для прохождения теста код должен быть равен 200
        self.assertEqual(response.status_code, 200)


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователя
        cls.user = User.objects.create_user(username='petr')
        cls.user2 = User.objects.create_user(username='lex')
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
            # author=User.objects.create(username='petr'),
        )
        cls.post2 = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user2
            # author=User.objects.create(username='lex'),
        )

    # Проверяем общедоступные страницы
    def test_index_url_all_users(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_posts_url_all_users(self):
        """Страница /group/<slug>/ доступна любому пользователю."""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_group_posts_url_authorised(self):
        """Страница /group/<slug>/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_new_posts_url_authorised(self):
        """Страница /new/ доступна авторизованному пользователю"""
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_urls_template(self):
        """Какой шаблон вызывается для страниц:"""
        templates_url_names = {
            'index.html': '/',
            'group.html': '/group/test-slug/',
            'new_post.html': '/new/',
            'post_new.html': f'/{self.user.username}/{self.post.id}/edit/'
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_profile_url_authorised(self):
        """Страница профайла пользователя доступна по /<username>/"""
        response = self.authorized_client.get('/petr/')
        self.assertEqual(response.status_code, 200)

    def test_post_view_url_authorised_id(self):
        """Страница профайла пользователя доступна по /<username>/<post_id>/"""
        response = self.authorized_client.get('/petr/1/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_guest(self):
        """Доступность страницы редактирования поста для гостя"""
        response = self.guest_client.get('/petr/1/edit/')
        self.assertEqual(response.status_code, 302)

    def test_post_edit_url_authorised_author(self):
        """Доступность страницы редактирования поста для автора поста"""
        response = self.authorized_client.get('/petr/1/edit/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_authorised_not_author(self):
        """Доступность страницы редактирования поста для не автора поста"""
        response = self.authorized_client.get('/lex/1/edit/')
        self.assertEqual(response.status_code, 404)

    def test_post_edit_redirect_not_author(self):
        """редирект со страницы /<username>/<post_id>/edit/для тех,
        у кого нет прав доступа к этой странице."""
        url = f'/{self.user.username}/{self.post2.id}/edit'
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, 301)

    def test_author_url_all_users(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_tech_url_all_users(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)
