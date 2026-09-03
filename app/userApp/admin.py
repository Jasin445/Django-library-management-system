from django.contrib import admin

from .models import Book, LibraryRecord, Student

class LibraryRecordInline(admin.TabularInline):
    model = LibraryRecord
    extra = 1

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "isbn",
        "available",
        "published_date",
        "created_at",
    )

    search_fields = (
        "title",
        "author",
        "isbn",
    )

    list_filter = (
        "available",
        "published_date",
    )

    ordering = ("-created_at",)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "level",
        "department",
    )

    search_fields = (
        "first_name",
        "last_name",
        "department",
    )

    list_filter = (
        "level",
        "department",
    )

    ordering = (
        "first_name",
        "last_name",
    )

    inlines = [LibraryRecordInline]  # noqa: RUF012


@admin.register(LibraryRecord)
class LibraryRecordAdmin(admin.ModelAdmin):
    list_display = (
        "book",
        "student",
        "borrowed_at",
        "due_at",
        "returned_at",
    )

    search_fields = (
        "book__title",
        "student__first_name",
        "student__last_name",
    )

    list_filter = (
        "borrowed_at",
        "due_at",
        "returned_at",
    )

    ordering = ("-borrowed_at",)