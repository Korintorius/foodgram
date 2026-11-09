from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


class User(AbstractUser):
    """Модель пользователя сервиса:
    - Вход по email,
    - Аватар."""

    email = models.EmailField(
        'адрес электронной почты',
        unique=True
    )
    avatar = models.ImageField(
        'аватар',
        upload_to='users/avatar/',
        blank=True,
        null=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('id',)

    def __str__(self):
        """Возвращение email пользователя."""
        return self.email


class Subscription(models.Model):
    """Подписка пользователя на автора рецептов."""

    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='автор',
    )
    created_at = models.DateTimeField('дата подписки', auto_now_add=True)

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'author'],
                name='subscription_unique',
                condition=Q(subscriber__isnull=False, author__isnull=False),
                violation_error_message='''Вы уже подписаны на этого
                пользователя''',
            ),
        ]
        ordering = ('id',)

    def __str__(self):
        """Возвращение комбинированной строки: подписчик - автор."""
        return f'{self.subscriber} -> {self.author}'
