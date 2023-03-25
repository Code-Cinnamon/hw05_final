import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.TestUser = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title="Тестовый заголовок",
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.group2 = Group.objects.create(
            title="Тестовый заголовок 2",
            slug='test-slug2',
            description='Тестовое описание 2',
        )

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.TestUser)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_authorized_client_post_create(self):
        """"Создается новый пост"""
        form_data = {
            'text': 'Данные из формы',
            'group': self.group.pk,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': post.author}))
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(post.author, self.TestUser)
        self.assertEqual(post.group, PostFormsTests.group)

    def test_guest_client_post_create(self):
        """"Неавторизованный клиент не может создавать посты."""
        form_data = {
            'text': 'Пост от неавторизованного клиента',
            'group': self.group.id
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        login_url = reverse('users:login')
        create_url = reverse('posts:post_create')
        self.assertRedirects(response, f'{login_url}?next={create_url}')
        self.assertEqual(Post.objects.count(), 0)

    def test_authorized_post_edit(self):
        """"Авторизованный клиент может редактировать посты."""
        post = Post.objects.create(
            text='Тестовый текст',
            author=self.TestUser,
            group=self.group,
        )
        form_data = {
            'text': 'Измененный текст',
            'group': self.group2.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}),
            data=form_data,
            follow=True
        )
        redirect = reverse(
            'posts:post_detail',
            kwargs={'post_id': post.pk}
        )
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(post.author, self.TestUser)
        self.assertEqual(post.group, self.group2)


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_form_create_comment(self):
        """Валидная форма создает запись в Comment."""
        comments_count = Comment.objects.count()
        form_data = {'text': 'Тестовый текст комментария'}
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
                author=self.user,
                post=self.post
            ).exists()
        )
