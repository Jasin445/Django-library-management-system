import json
import uuid

from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt

from userApp.models import Book, LibraryRecord, Student


# Create your views here.
def home(request):
    return JsonResponse({"message": "Hello world", "version": "v.1.0"})


@csrf_exempt
def create_book(request):
    if request.method != "POST":
        return JsonResponse({"status": 405, "error": "Method not allowed"}, status=405)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": 400, "error": "JSON decode Error"}, status=400)

    title = payload.get("title")
    author = payload.get("author")
    description = payload.get("description")
    isbn = payload.get("isbn")
    published_date = payload.get("published_date")
    available = payload.get("available")
    if available is not None:
        available = available  # noqa: PLW0127
    else:
        available = True

    if (
        title is None
        or author is None
        or description is None
        or isbn is None
        or published_date is None
    ):
        return JsonResponse(
            {
                "status": 400,
                "error": "title, author, description, isbn, published_date are all required!",
                "message": "Bad request",
            },
            status=400,
        )

    kwargs = {
        "title": title,
        "author": author,
        "description": description,
        "isbn": isbn,
        "published_date": published_date,
        "available": available,
    }

    created_book = Book.objects.create(**kwargs)

    book_data = {
        "id": created_book.id,
        "title": created_book.title,
        "author": created_book.author,
        "description": created_book.description,
        "isbn": created_book.isbn,
        "published_date": created_book.published_date,
        "available": created_book.available,
    }
    print(created_book)

    return JsonResponse(
        {
            "status": 201,
            "message": "Book created successfully",
            "book": book_data,
        },
        status=201,
    )


def get_all_books(request):
    books = Book.objects.all().values()

    if not books.exists():
        return JsonResponse(
            {
                "status": 200,
                "message": "No books currently in the shelf",
                "books": [],
            },
            status=200,
        )

    return JsonResponse(
        {
            "status": 200,
            "message": "Books fetched successfully",
            "books": list(books),
        },
        status=200,
    )


@csrf_exempt
def register_student(request):
    if request.method != "POST":
        return JsonResponse({"status": 405, "error": "Method not allowed"}, status=405)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": 400, "error": "JSON decode Error"}, status=400)

    first_name = payload.get("first_name")
    last_name = payload.get("last_name")
    level = payload.get("level")
    department = payload.get("department")

    if first_name is None or last_name is None or level is None or department is None:
        return JsonResponse(
            {
                "status": 400,
                "error": "first_name, last_name, level, department are all required!",
                "message": "Bad request",
            },
            status=400,
        )

    kwargs = {
        "first_name": first_name,
        "last_name": last_name,
        "level": level,
        "department": department,
    }

    registered_student = Student.objects.create(**kwargs)

    student_data = {
        "id": str(registered_student.id),
        "first_name": registered_student.first_name,
        "last_name": registered_student.last_name,
        "level": registered_student.level,
        "department": registered_student.department,
    }

    return JsonResponse(
        {
            "status": 200,
            "message": "Books registered successfully",
            "student": student_data,
        },
        status=200,
    )


def get_all_students(request):
    students = Student.objects.all().values()

    if not students.exists():
        return JsonResponse(
            {
                "status": 200,
                "message": "No Student currently has enrolled",
                "students": [],
            },
            status=200,
        )

    return JsonResponse(
        {
            "status": 200,
            "message": "Students fetched successfully",
            "students": list(students),
        },
        status=200,
    )


@csrf_exempt
def borrow_book(request):
    if request.method != "POST":
        return JsonResponse({"status": 405, "error": "Method not allowed"}, status=405)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": 400, "error": "JSON decode Error"}, status=400)

    book_id = payload.get("book_id")
    student_id = payload.get("student_id")
    due_at = payload.get("due_at")

    if book_id is None or student_id is None or due_at is None:
        return JsonResponse(
            {
                "status": 400,
                "error": "book_id, student_id, due_at are all required!",
                "message": "Bad request",
            },
            status=400,
        )

    due_at = parse_date(due_at)

    if due_at is None:
        return JsonResponse(
            {
                "status": 400,
                "error": "You must enter a valid date",
                "message": "Bad request",
            },
            status=400,
        )

    try:
        book_id = int(book_id)
    except (ValueError, TypeError):
        return JsonResponse(
            {
                "status": 400,
                "error": "book_id must be a valid integer!",
                "message": "Bad request",
            },
            status=400,
        )

    try:
        student_id = uuid.UUID(str(student_id))
    except (ValueError, TypeError, AttributeError):
        return JsonResponse(
            {
                "status": 400,
                "error": "student_id must be a valid UUID!",
                "message": "Bad request",
            },
            status=400,
        )
    try:
        target_student = get_object_or_404(Student, id=student_id)
    except Http404:
        return JsonResponse(
            {
                "status": 404,
                "error": "A student with this ID does not exist!",
                "message": "Bad request",
            },
            status=404,
        )

    with transaction.atomic():
        try:
            target_book = Book.objects.select_for_update().get(id=book_id)
        except Book.DoesNotExist:
            return JsonResponse(
                {
                    "status": 404,
                    "error": "A book with this ID does not exist!",
                    "message": "Bad request",
                },
                status=404,
            )

        if not target_book.available:
            active_record = LibraryRecord.objects.filter(
                book=target_book, returned_at__isnull=True
            ).first()

            if active_record and active_record.student.id == student_id:
                return JsonResponse(
                    {
                        "status": 409,
                        "error": "This book was borrowed by you and has not been returned yet",
                        "message": "Conflict",
                    },
                    status=409,
                )

            if active_record:
                return JsonResponse(
                    {
                        "status": 409,
                        "error": f"This book was borrowed by {active_record.student.first_name + ' ' + active_record.student.last_name} and has not been returned yet",
                        "message": "Conflict",
                    },
                    status=409,
                )

            return JsonResponse(
                {
                    "status": 409,
                    "error": "This book is marked unavailable but has no active borrow record. Please contact an administrator.",
                    "message": "Conflict",
                },
                status=409,
            )

        record = LibraryRecord.objects.create(
            book=target_book,
            student=target_student,
            due_at=due_at,
        )
        target_book.available = False
        target_book.save()

    borrowed_data = {
        "id": record.id,
        "book_id": record.book_id,
        "student_id": record.student_id,
        "borrowed_at": record.borrowed_at,
        "due_at": record.due_at,
        "returned_at": record.returned_at,
    }

    return JsonResponse(
        {
            "status": 200,
            "message": "Book borrowed successfully",
            "record": borrowed_data,
        },
        status=200,
    )


def getBorrowedBookById(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    borrowed_records = LibraryRecord.objects.filter(book=book)

    if not borrowed_records.exists():
        return JsonResponse(
            {
                "status": 404,
                "error": "No record found for this book_id",
            },
            status=404,
        )

    book_data = {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "description": book.description,
        "isbn": book.isbn,
        "published_date": book.published_date,
        "available": book.available,
    }

    borrowed_data = list(borrowed_records.values())

    return JsonResponse(
        {
            "status": 200,
            "book": book_data,
            "borrowed_records": borrowed_data,
            "message": "Book details and borrowed records fetched successfully",
        }
    )


def get_all_borrowed_books(request):
    borrowed_records = LibraryRecord.objects.filter(returned_at__isnull=True).values()
    print(borrowed_records)

    if not borrowed_records.exists():
        return JsonResponse(
            {
                "status": 200,
                "message": "No books are currently borrowed",
                "borrowed_books": [],
            },
            status=200,
        )

    return JsonResponse(
        {
            "status": 200,
            "message": "Borrowed books fetched successfully",
            "borrowed_books": list(borrowed_records),
        },
        status=200,
    )


@csrf_exempt
def return_borrowed_book(request):
    if request.method != "POST":
        return JsonResponse(
            {
                "status": 405,
                "error": "Method not allowed!",
                "message": "Not allowed",
            },
            status=405,
        )

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": 400, "error": "JSON decode Error"}, status=400)

    book_id = payload.get("book_id")
    student_id = payload.get("student_id")

    if book_id is None or student_id is None:
        return JsonResponse(
            {
                "status": 400,
                "error": "book_id and student_id are required!",
                "message": "Bad request",
            },
            status=400,
        )
    try:
        book = get_object_or_404(Book, id=book_id)
        student = get_object_or_404(Student, id=student_id)
    except Http404:
        return JsonResponse(
            {
                "status": 400,
                "error": "Book or student not found!",
                "message": "Bad request",
            },
            status=400,
        )

    book_record = LibraryRecord.objects.filter(
        book=book, student=student, returned_at__isnull=True
    ).first()

    if not book_record:
        return JsonResponse(
            {
                "status": 404,
                "error": "you currently didn't borrow any book with this id!",
                "message": "Not Found",
            },
            status=404,
        )

    with transaction.atomic():
        book_record.returned_at = timezone.now()
        book_record.save()
        book.available = True
        book.save()

    return JsonResponse(
        {
            "status": 200,
            "message": "Borrowed books returned successfully",
            "returned_book": {
                "id": book.id,
                "title": book.title,
                "isbn": book.isbn,
                "description": book.description,
                "returned_at": book_record.returned_at,
            },
        },
        status=200,
    )


@csrf_exempt
def delete_book(request, book_id: int):
    if request.method != "DELETE":
        return JsonResponse(
            {
                "status": 405,
                "error": "Method not allowed!",
                "message": "Not allowed",
            },
            status=405,
        )

    book = Book.objects.filter(id=book_id).first()

    if not book:
        return JsonResponse(
            {
                "status": 404,
                "error": "No book with this ID was found",
            },
            status=404,
        )

    book.delete()

    return JsonResponse(
        {
            "status": 200,
            "message": "This Book has been deleted successfully!",
        },
        status=200,
    )
