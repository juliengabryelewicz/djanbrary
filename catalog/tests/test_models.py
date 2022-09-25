
from django.test import TestCase

# Create your tests here.

from catalog.models import Author, Category, Book


class AuthorModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Author.objects.create(first_name='Big', last_name='Bob')

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEqual(field_label, 'first name')

    def test_last_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('last_name').verbose_name
        self.assertEqual(field_label, 'last name')

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEqual(max_length, 100)

    def test_last_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('last_name').max_length
        self.assertEqual(max_length, 100)

    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = '{0}, {1}'.format(author.last_name, author.first_name)

        self.assertEqual(str(author), expected_object_name)

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        self.assertEqual(author.get_absolute_url(), '/catalog/author/1')

class CategoryModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Category.objects.create(name='Fantastique')

    def test_name_label(self):
        category = Category.objects.get(id=1)
        field_label = category._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_name_max_length(self):
        category = Category.objects.get(id=1)
        max_length = category._meta.get_field('name').max_length
        self.assertEqual(max_length, 200)

class BookModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        test_author = Author.objects.create(first_name='J.R.R', last_name='Tolkien')
        Category.objects.create(name='Fantastique')
        test_book = Book.objects.create(
            title='Le Seigneur des Anneaux',
            year='1900',
            content='Le livre adapté au cinéma en 2001',
            isbn='1234567890',
            author=test_author,
        )
        test_category = Category.objects.filter(id=1)
        test_book.category.set(test_category)
        test_book.save()

    def test_title_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')

    def test_name_max_length(self):
        book = Book.objects.get(id=1)
        max_length = book._meta.get_field('title').max_length
        self.assertEqual(max_length, 200)

    def test_author_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('author').verbose_name
        self.assertEqual(field_label, 'author')

    def test_year_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('year').verbose_name
        self.assertEqual(field_label, 'Year')

    def test_content_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('content').verbose_name
        self.assertEqual(field_label, 'content')

    def test_content_max_length(self):
        book = Book.objects.get(id=1)
        max_length = book._meta.get_field('content').max_length
        self.assertEqual(max_length, 1000)
