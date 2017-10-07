import uuid

from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify

from .constants import cat_name_max_length, page_title_max_length, integer_default_views_and_likes, url_max_length


class UserProfile(models.Model):
    # custom user profile class
    # linked to django.contrib.auth.models.User
    user = models.OneToOneField(User)

    # additional attributes
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return self.user.username

    def get_username(self):
        return self.user.username

    def get_email(self):
        return self.user.email

    def get_lname(self):
        return self.user.last_name

    def get_fname(self):
        return self.user.first_name


class Category(models.Model):
    name = models.CharField(max_length=cat_name_max_length, unique=True)
    views = models.IntegerField(default=integer_default_views_and_likes)
    likes = models.IntegerField(default=integer_default_views_and_likes)
    slug = models.SlugField(unique=True, default=uuid.uuid1())  # prettify urls avoiding spaces

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

    def pages_count(self):
        return self.page_set.count()

    pages_count.admin_order_field = 'page'


class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=page_title_max_length)
    url = models.URLField(max_length=url_max_length)
    views = models.IntegerField(default=integer_default_views_and_likes)

    def __str__(self):
        return self.title
