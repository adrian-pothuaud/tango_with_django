from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from rango.forms import CategoryForm, PageForm, UserProfileForm
from rango.webhose_search import run_query
from .constants import integer_default_views_and_likes
from .models import Category, Page, UserProfile


# A helper method
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request,
                                               'last_visit',
                                               str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')

    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # Update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        visits = 1
        # Set the last visit cookie
        request.session['last_visit'] = last_visit_cookie

    # Update/set the visits cookie
    request.session['visits'] = visits


def index(request):
    # test cookies
    request.session.set_test_cookie()
    # get top 5 categories
    top_categories = Category.objects.order_by('-likes')[:5]
    top_pages = Page.objects.order_by('-views')[:5]
    visitor_cookie_handler(request)
    # dictionary to pass to the template
    context_dict = {'boldmessage': 'Hello from Rango !',
                    'top_categories': top_categories,
                    'top_pages': top_pages,
                    'visits': request.session['visits']}

    # get response early to set cookies
    return render(request, 'rango/index.html', context=context_dict)


def about(request):
    # test cookies
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()
    # dictionary to pass to the template
    context_dict = {'boldmessage': 'Hello from About Rango !'}

    visitor_cookie_handler(request)
    count = request.session.get('visits', 0)
    context_dict['visit_count'] = count

    # return a rendered response to the client
    return render(request, 'rango/about.html', context=context_dict)


def show_category(request, category_name_slug):
    context_dict = dict()

    category = get_object_or_404(Category, slug=category_name_slug)
    context_dict['category'] = category

    pages = Page.objects.filter(category=category).order_by('-views')
    context_dict['pages'] = pages

    context_dict['query'] = category.name

    if request.method == 'POST':

        query = request.POST['query'].strip()

        if query:
            # Run our search API function to get the results list!
            result_list = run_query(query)
            context_dict['query'] = query
            context_dict['result_list'] = result_list

    # GET
    return render(request, 'rango/category.html', context_dict)


def get_category_list(max_results=0, starts_with=''):
    if len(starts_with):
        cat_list = Category.objects.filter(name__istartswith=starts_with)
    else:
        cat_list = Category.objects.all()
    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]
    return cat_list


def suggest_category(request):
    starts_with = ''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']
    cat_list = get_category_list(8, starts_with)
    return render(request, 'rango/cats.html', {'cats': cat_list})


def search(request):
    result_list = []
    query = None
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            # Run our Webhose search function to get the results list!
            result_list = run_query(query)
    return render(request, 'rango/search.html', {'result_list': result_list, 'query': query})


def track_url(request, page_id):
    page = get_object_or_404(Page, pk=page_id)
    page.views += 1
    page.save()
    return redirect(page.url)


@login_required
def register_profile(request):
    form = UserProfileForm()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)

        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            return redirect('rango:index')

        print(form.errors)

    context_dict = {'form': form}
    return render(request, 'rango/profile_registration.html', context_dict)


@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('rango:index')

    userprofile = UserProfile.objects.get_or_create(user=user)[0]
    form = UserProfileForm(
        {'website': userprofile.website, 'picture': userprofile.picture}
    )
    if request.method == 'POST' and user == request.user:
        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)

        if form.is_valid():
            form.save(commit=True)
            return redirect('rango:profile', user.username)
        else:
            print(form.errors)

    return render(request, 'rango/profile.html', {
        'userprofile': userprofile,
        'selecteduser': user,
        'form': form
    })


@login_required
def list_profiles(request):
    userprofile_list = UserProfile.objects.all()
    return render(request, 'rango/list_profiles.html',
                  {'userprofile_list': userprofile_list}
                  )


@login_required
def like_category(request):
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        likes = 0
        if cat_id:
            cat = Category.objects.get(id=int(cat_id))
            if cat:
                likes = cat.likes + 1
                cat.likes = likes
                cat.save()
        return HttpResponse(likes)


"""
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
    return render(request, 'rango/unused_register.html', {
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
    return render(request, 'rango/unused_login.html', {'errors': errors})
    
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('rango:index'))

"""


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
            return redirect('rango:show_category', category.slug)

        print(form.errors)

    context_dict = {'form': form, 'category': category, 'query': None}
    return render(request, 'rango/add_page.html', context=context_dict)
