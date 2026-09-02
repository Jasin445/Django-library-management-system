from django.urls import path

from . import views

urlpatterns = [
    path("", views.home),
    path("create-book/", views.create_book),
    path("get-all-books/", views.get_all_books),
    path("get-borrowed-book/<int:book_id>/", views.getBorrowedBookById),
    path("get-all-borrowed-books/", views.get_all_borrowed_books),
    path("register-student/", views.register_student),
    path("get-all-students/", views.get_all_students),
    path("borrow-book/", views.borrow_book),
    path("delete-book/<int:book_id>/", views.delete_book),
    path("return-borrowed-book/", views.return_borrowed_book),
]