from django.contrib import admin

from .models import Author, Category, Book, BookAvailability

admin.site.register(Category)

class BooksAvailabilityInline(admin.TabularInline):
    model = BookAvailability

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name')
    fields = ['first_name', 'last_name', 'biography']
    pass

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_category')
    inlines = [BooksAvailabilityInline]
    pass

@admin.register(BookAvailability)
class BookAvailabilityAdmin(admin.ModelAdmin):
    list_filter = ('status', 'due_back')
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back','borrower')
        }),
    )
    pass
