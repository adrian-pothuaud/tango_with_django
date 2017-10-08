from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from rango.forms import CategoryForm, PageForm
from rango.webhose_search import run_query
from .constants import integer_default_views_and_likes
from .models import Category, Page


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
    # dictionary to pass to the template
    context_dict = dict()
    category = get_object_or_404(Category, slug=category_name_slug)
    pages = Page.objects.filter(category=category)
    context_dict['category'] = category
    context_dict['pages'] = pages
    return render(request, 'rango/category.html', context=context_dict)


def search(request):
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            # Run our Webhose search function to get the results list!
            result_list = run_query(query)
    return render(request, 'rango/search.html', {'result_list': result_list,
                                                 'query': query, })


def track_url(request, page_id):
    page = get_object_or_404(Page, pk=page_id)
    page.views += 1
    page.save()
    return redirect(page.url)


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

            return show_category(request, category.slug)

        print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)
