from django.contrib.auth.models import User
from django.forms import models
from django import forms

from rango.models import Category, Page, UserProfile

from .constants import cat_name_max_length, page_title_max_length, integer_default_views_and_likes, url_max_length


class UserForm(models.ModelForm):
    # attributes
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(models.ModelForm):
    # attributes

    class Meta:
        model = UserProfile
        fields = ('website', 'picture')


class CategoryForm(models.ModelForm):
    name = forms.CharField(max_length=cat_name_max_length,
                           help_text="Please enter the Category name")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=integer_default_views_and_likes)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=integer_default_views_and_likes)
    slug = forms.CharField(widget=forms.HiddenInput, required=False)

    # an inline class to define additional information on the form
    class Meta:
        model = Category
        fields = ('name',)


class PageForm(models.ModelForm):
    title = forms.CharField(max_length=page_title_max_length,
                            help_text="Please enter the Page title")
    url = forms.URLField(max_length=url_max_length,
                         help_text="Please enter the url of the Page")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=integer_default_views_and_likes)

    # an inline class to define additional information on the form
    class Meta:
        model = Page
        exclude = ('category', )

    # override clean method called right before save
    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        if url and not url.startswith('http://'):
            url = 'http://' + url
            cleaned_data['url'] = url

        return cleaned_data
