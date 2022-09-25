import uuid 
import datetime
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

def current_year():
    return datetime.date.today().year

class Category(models.Model):
    name = models.CharField(max_length=200, help_text='Entrez une catégorie de livre')

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    year = models.IntegerField('Year', default=current_year, help_text='Année de publication')
    content = models.TextField(max_length=1000, help_text='Décrivez le livre')
    isbn = models.CharField('ISBN', max_length=13, unique=True, help_text='Maximum 13 caractères')
    category = models.ManyToManyField(Category, help_text='Choisissez une catégorie')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])

    def display_category(self):
        return ', '.join([category.name for category in self.category.all()[:3]])

    display_category.short_description = 'Category'

class BookAvailability(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Identifiant unique à la librairie")
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_overdue(self):
        return bool(self.due_back and datetime.date.today() > self.due_back)

    LOAN_STATUS = (
        ('d', 'En attente'),
        ('o', 'En location'),
        ('a', 'Disponible'),
        ('r', 'Réservé'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='d',
        help_text='Disponibilité du livre')

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Peut indiquer le livre comme rendu"),)

    def __str__(self):
        return '{0} ({1})'.format(self.id, self.book.title)


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    biography = models.TextField(max_length=1000, help_text='Décrivez une petit biographie')

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return '{0}, {1}'.format(self.last_name, self.first_name)