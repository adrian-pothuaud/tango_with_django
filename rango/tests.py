from django.test import TestCase
from rango.models import Category
from django.core.urlresolvers import reverse


class CategoryMethodTests(TestCase):
    def test_ensure_views_are_positive(self):
        """
        ensure_views_are_positive should results True for categories
        where views are zero or positive
        """
        cat = Category(name='test', views=-1, likes=0)
        cat.save()
        self.assertEqual((cat.views >= 0), True)

    def test_slug_line_creation(self):
        """
        slug_line_creation checks to make sure that when we add
        a category an appropriate slug line is created
        i.e. "Random Category String" -> "random-category-string"
        """
        cat = Category.objects.create(name='Random Category String')
        cat.save()
        self.assertEqual(cat.slug, 'random-category-string')


class IndexViewTests(TestCase):
    def test_index_view_with_no_categories(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('rango:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no categories present.")
        self.assertQuerysetEqual(response.context['categories'], [])
