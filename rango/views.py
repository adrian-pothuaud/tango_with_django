from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from .models import Category, Page
from .constants import integer_default_views_and_likes


def index(request):
    # get top 5 categories
    top_categories = Category.objects.order_by('-likes')[:5]
    top_pages = Page.objects.order_by('-views')[:5]
    # dictionary to pass to the template
    context_dir = {'boldmessage': 'Hello from Rango !',
                   'top_categories': top_categories,
                   'top_pages': top_pages, }

    # return a rendered response to the client
    return render(request, 'rango/index.html', context=context_dir)


def about(request):
    # dictionary to pass to the template
    context_dir = {'boldmessage': 'Hello from About Rango !'}

    # return a rendered response to the client
    return render(request, 'rango/about.html', context=context_dir)


def show_category(request, category_name_slug):
    # dictionary to pass to the template
    context_dir = dict()
    category = get_object_or_404(Category, slug=category_name_slug)
    pages = Page.objects.filter(category=category)
    context_dir['category'] = category
    context_dir['pages'] = pages
    return render(request, 'rango/category.html', context=context_dir)


def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            registered = True

        print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request, 'rango/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered
    })


def user_login(request):
    errors = None
    if request.method == 'POST':
        # POST
        # as opposed to request.POST['username']
        # request.POST.get() will return None if there is an error
        username = request.POST.get('username')
        password = request.POST.get('password')
        # verify authentication with Django provided authentication system
        # returns a User if anything OK
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                auth_login(request, user)
                return HttpResponseRedirect(reverse('rango:index'))
            return HttpResponse('Your Rango account is disabled !')
        print("Invalid login details: {0}, {1}".format(username, password))
        if not errors:
            errors = dict()
        errors['invalid login'] = "Invalid login details"
    # GET
    return render(request, 'rango/login.html', {'errors': errors})


@login_required
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)

            return index(request)

        print(form.errors)

    return render(request, 'rango/add_category.html', context={'form': form, })


@login_required
def add_page(request, category_slug_name):
    category = get_object_or_404(Category, slug=category_slug_name)

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            page = form.save(commit=False)

            page.category = category
            page.views = integer_default_views_and_likes
            page.save()

            return show_category(request, category.slug)

        print(form.errors)

    context_dic = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dic)


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('rango:index'))
