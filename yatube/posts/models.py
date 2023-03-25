from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу',
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        verbose_name="Картинка",
        help_text="Добавьте иллюстрацию к посту. Необязательное поле"
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментируемый пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments_of_author',
        verbose_name='Автор комментария'
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Введите текст комментария'
    )
    created = models.DateTimeField(
        'Дата публикации комментария',
        auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик')

    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Подписка'
    )

    def __str__(self):
        return f'{self.user.username} --> {self.author.username}'

    class Meta:
        unique_together = ['user', 'author']
