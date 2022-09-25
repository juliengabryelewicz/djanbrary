from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from .models import Book, Author, BookAvailability, Category
from catalog.forms import RenewBookForm
import datetime

def index(request):
 
    num_books = Book.objects.all().count()
    num_availabilities = BookAvailability.objects.all().count()

    num_availabilities_open = BookAvailability.objects.filter(status__exact='a').count()

    num_authors = Author.objects.count()

    context = {
        'num_books': num_books,
        'num_availabilities': num_availabilities,
        'num_availabilities_open': num_availabilities_open,
        'num_authors': num_authors,
    }

    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookAvailability
    template_name = 'catalog/bookavailability_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookAvailability.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    model = BookAvailability
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookavailability_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookAvailability.objects.filter(status__exact='o').order_by('due_back')

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_availability = get_object_or_404(BookAvailability, pk=pk)

    if request.method == 'POST':

        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_availability.due_back = form.cleaned_data['renewal_date']
            book_availability.save()

            return HttpResponseRedirect(reverse('all-borrowed'))
            
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_availability': book_availability,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'biography']
    permission_required = 'catalog.can_mark_returned'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'biography']
    permission_required = 'catalog.can_mark_returned'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'year', 'content', 'isbn', 'category']
    permission_required = 'catalog.can_mark_returned'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'year', 'content', 'isbn', 'category']
    permission_required = 'catalog.can_mark_returned'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_returned'