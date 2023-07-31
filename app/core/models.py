from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin)

from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email: str, name: str, password: str = None):
        if not email:
            raise ValueError("User should have an email.")

        user = self.model(
            email=self.normalize_email(email),
            name=name
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email: str, name: str, password: str = None):
        user = self.create_user(email, name, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email


class Review(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    rating = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Book(models.Model):
    title = models.CharField(max_length=255)
    publication_date = models.DateField()
    isbn = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    publishers = models.ManyToManyField('Publisher')
    reviews = models.ManyToManyField('Review')

    def __str__(self):
        return self.title


class Publisher(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField(max_length=255)
    email = models.EmailField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
