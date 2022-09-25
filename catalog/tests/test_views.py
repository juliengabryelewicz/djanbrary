from django.test import TestCase

# Create your tests here.


import datetime
from django.utils import timezone

from catalog.models import BookAvailability, Book, Category, Author
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.urls import reverse
import uuid


class AuthorListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        number_of_authors = 13
        for author_id in range(number_of_authors):
            Author.objects.create(first_name='Andrzej {0}'.format(author_id),
                                  last_name='Sapkowski {0}'.format(author_id))

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertEqual(len(response.context['author_list']), 10)

    def test_lists_all_authors(self):
        # Get second page and confirm it has (exactly) the remaining 3 items
        response = self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertEqual(len(response.context['author_list']), 3)




class LoanedBookAvailabilitiesByUserListViewTest(TestCase):

    def setUp(self):
        test_user1 = User.objects.create_user(username='user1', password='user1')
        test_user2 = User.objects.create_user(username='user2', password='user2')

        test_user1.save()
        test_user2.save()

        test_author = Author.objects.create(first_name='Andrzej', last_name='Sapkowski')
        test_category = Category.objects.create(name='Fantastique')
        test_book = Book.objects.create(
            title='The Witcher',
            year='1989',
            content='Suivez les aventures du sorceleur Geralt de Riv',
            isbn='2134567890',
            author=test_author,
        )

        category_objects_for_book = Category.objects.all()
        test_book.category.set(category_objects_for_book)
        test_book.save()

        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.now() + datetime.timedelta(days=book_copy % 5)
            if book_copy % 2:
                the_borrower = test_user1
            else:
                the_borrower = test_user2
            status = 'm'
            BookAvailability.objects.create(book=test_book, imprint='Plon, 2016', due_back=return_date,
                                        borrower=the_borrower, status=status)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('my-borrowed'))

        self.assertEqual(str(response.context['user']), 'user1')
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'catalog/bookavailability_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('my-borrowed'))

        self.assertEqual(str(response.context['user']), 'user1')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('bookavailability_list' in response.context)
        self.assertEqual(len(response.context['bookavailability_list']), 0)

        get_ten_books = BookAvailability.objects.all()[:10]

        for copy in get_ten_books:
            copy.status = 'o'
            copy.save()

        response = self.client.get(reverse('my-borrowed'))
        self.assertEqual(str(response.context['user']), 'user1')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('bookavailability_list' in response.context)
        for bookitem in response.context['bookavailability_list']:
            self.assertEqual(response.context['user'], bookitem.borrower)
            self.assertEqual(bookitem.status, 'o')

    def test_pages_paginated_to_ten(self):

        for copy in BookAvailability.objects.all():
            copy.status = 'o'
            copy.save()

        login = self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('my-borrowed'))

        self.assertEqual(str(response.context['user']), 'user1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['bookavailability_list']), 10)

    def test_pages_ordered_by_due_date(self):

        for copy in BookAvailability.objects.all():
            copy.status = 'o'
            copy.save()

        login = self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('my-borrowed'))

        self.assertEqual(str(response.context['user']), 'user1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['bookavailability_list']), 10)

        last_date = 0
        for copy in response.context['bookavailability_list']:
            if last_date == 0:
                last_date = copy.due_back
            else:
                self.assertTrue(last_date <= copy.due_back)

class RenewBookAvailabilitiesViewTest(TestCase):

    def setUp(self):
        test_user1 = User.objects.create_user(username='user1', password='user1')
        test_user1.save()

        test_user2 = User.objects.create_user(username='user2', password='user2')
        test_user2.save()
        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        test_author = Author.objects.create(first_name='Andrzej', last_name='Sapkowski')
        test_category = Category.objects.create(name='Fantastique')
        test_book = Book.objects.create(title='The Witcher', content='Les aventures de Geralt de Riv', year='1989',
                                        isbn='ABCDEFG', author=test_author)

        category_objects_for_book = Category.objects.all()
        test_book.category.set(category_objects_for_book)
        test_book.save()

        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookavailability1 = BookAvailability.objects.create(book=test_book,
                                                              imprint='Plon, 2016', due_back=return_date,
                                                              borrower=test_user1, status='o')

        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookavailability2 = BookAvailability.objects.create(book=test_book, imprint='Plon, 2016',
                                                              due_back=return_date, borrower=test_user2, status='o')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookavailability1.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookavailability1.pk}))
        self.assertEqual(response.status_code, 403)


    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='user2', password='user2')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookavailability2.pk}))

        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username='user2', password='user2')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookavailability1.pk}))

        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='user2', password='user2')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookavailability1.pk}))
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'catalog/book_renew_librarian.html')

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='user2', password='user2')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookavailability1.pk}))
        self.assertEqual(response.status_code, 200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(response.context['form'].initial['renewal_date'], date_3_weeks_in_future)

    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(username='user2', password='user2')

        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookavailability1.pk}),
                                    {'renewal_date': date_in_past})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'renewal_date', "Date invalide - Date antérieur à aujourd'hui")

    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(username='user2', password='user2')
        
        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
        response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookavailability1.pk}),
                                    {'renewal_date': invalid_date_in_future})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'renewal_date', "Date invalide - Vous ne pouvez pas aller au-delà du mois prochain")

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(username='user2', password='user2')
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookavailability1.pk}),
                                    {'renewal_date': valid_date_in_future})
        self.assertRedirects(response, reverse('all-borrowed'))

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        test_uid = uuid.uuid4()
        login = self.client.login(username='user2', password='user2')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': test_uid}))
        self.assertEqual(response.status_code, 404)


class AuthorCreateViewTest(TestCase):

    def setUp(self):
        test_user1 = User.objects.create_user(username='user1', password='user1')
        test_user2 = User.objects.create_user(username='user2', password='user2')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        test_author = Author.objects.create(first_name='John', last_name='Smith')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('author-create'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/author/create/')

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission(self):
        login = self.client.login(username='user2', password='user2')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='user2', password='user2')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_form.html')