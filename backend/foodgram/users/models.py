from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password')
    email = models.EmailField(
        max_length=250,
        unique=True,
        verbose_name='email',
    )
    username = models.CharField(
        blank=False,
        max_length=150,
        unique=True,
        verbose_name='username',
        validators=(RegexValidator(regex=r'^[\w.@+-]+\Z'),),
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'User'
