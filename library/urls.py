"""
URL configuration for the library application.  These URL patterns
dispatch requests to the corresponding view functions defined in
``views.py``.  They are included in the project's root URLConf via
``include()``.
"""

from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("books/<int:pk>/", views.book_detail, name="book_detail"),
    path("books/<int:pk>/reserve/", views.reserve_book, name="reserve_book"),
    path(
        "books/<int:pk>/purchase/", views.purchase_book, name="purchase_book"
    ),
    path("reservations/", views.user_reservations, name="user_reservations"),
    path("purchases/", views.user_purchases, name="user_purchases"),
    path(
        "reservations/<int:res_id>/cancel/",
        views.cancel_reservation,
        name="cancel_reservation",
    ),
    path(
        "reservations/<int:res_id>/return/",
        views.return_book,
        name="return_book",
    ),
    path("register/", views.register, name="register"),
]