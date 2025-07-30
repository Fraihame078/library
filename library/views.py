"""
Представления для сайта библиотеки.

Здесь определены функции, которые отвечают за отображение страниц,
создание бронирований, покупок и регистрацию пользователей.  Код
написан максимально просто — без сложных классов и миксинов.
"""

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import UserRegistrationForm
from .models import Book, Reservation
from .models import Purchase


def home(request):
    """Display a list of all books."""
    books = Book.objects.all()
    return render(request, "library/home.html", {"books": books})


def book_detail(request, pk: int):
    """Display detailed information for a single book."""
    book = get_object_or_404(Book, pk=pk)
    # Determine if the current user has already purchased this VIP book
    user_has_purchased = False
    if request.user.is_authenticated and book.is_vip:
        user_has_purchased = Purchase.objects.filter(
            user=request.user, book=book
        ).exists()
    context = {
        "book": book,
        "user_has_purchased": user_has_purchased,
    }
    return render(request, "library/book_detail.html", context)


def register(request):
    """Handle user registration and automatically log the new user in."""
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically log in the new user
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect("home")
    else:
        form = UserRegistrationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def reserve_book(request, pk: int):
    """
    Reserve a book for the logged‑in user.  If no copies are available or
    the user already has an active reservation, display an error.
    """
    book = get_object_or_404(Book, pk=pk)
    # Disallow reservations for VIP books
    if book.is_vip:
        messages.error(
            request, "Эту книгу нельзя бронировать, она находится в VIP разделе."
        )
        return redirect("book_detail", pk=pk)
    if not book.is_available():
        messages.error(request, "Нет доступных экземпляров этой книги.")
        return redirect("book_detail", pk=pk)
    # Prevent multiple active reservations for the same book
    existing_res = Reservation.objects.filter(
        user=request.user, book=book, status="reserved"
    )
    if existing_res.exists():
        messages.error(request, "Вы уже зарезервировали эту книгу.")
        return redirect("book_detail", pk=pk)
    # Create reservation and reduce available copies
    Reservation.objects.create(user=request.user, book=book)
    book.available_copies -= 1
    book.save()
    messages.success(request, "Книга успешно зарезервирована.")
    return redirect("user_reservations")


@login_required
def purchase_book(request, pk: int):
    """
    Allow a user to purchase a VIP book.  If the book is not in the VIP
    section or has already been purchased by the user, redirect with an
    appropriate message.
    """
    book = get_object_or_404(Book, pk=pk)
    if not book.is_vip:
        messages.error(request, "Эта книга не находится в VIP разделе.")
        return redirect("book_detail", pk=pk)
    # Check if already purchased
    if Purchase.objects.filter(user=request.user, book=book).exists():
        messages.info(request, "Вы уже приобрели эту книгу.")
        return redirect("book_detail", pk=pk)
    # Create purchase record with the book's price (or zero if not set)
    price = book.price or 0
    Purchase.objects.create(user=request.user, book=book, price=price)
    messages.success(request, "Книга успешно куплена!")
    return redirect("user_purchases")


@login_required
def user_purchases(request):
    """List all VIP book purchases for the logged‑in user."""
    purchases = request.user.purchases.order_by("-purchased_at")
    return render(
        request,
        "library/user_purchases.html",
        {"purchases": purchases},
    )


@login_required
def user_reservations(request):
    """List all reservations for the logged‑in user."""
    reservations = request.user.reservations.order_by("-reserved_at")
    return render(
        request,
        "library/user_reservations.html",
        {"reservations": reservations},
    )


@login_required
def cancel_reservation(request, res_id: int):
    """Allow a user to cancel a reservation if it is still active."""
    reservation = get_object_or_404(
        Reservation, pk=res_id, user=request.user
    )
    if reservation.status == "reserved":
        reservation.status = "cancelled"
        reservation.save()
        # Return the book copy to availability
        reservation.book.available_copies += 1
        reservation.book.save()
        messages.success(request, "Бронирование отменено.")
    else:
        messages.info(request, "Это бронирование уже закрыто.")
    return redirect("user_reservations")


@login_required
def return_book(request, res_id: int):
    """Mark a reservation as returned and set the return date."""
    reservation = get_object_or_404(
        Reservation, pk=res_id, user=request.user
    )
    if reservation.status == "reserved":
        reservation.status = "returned"
        reservation.return_date = timezone.now().date()
        reservation.save()
        reservation.book.available_copies += 1
        reservation.book.save()
        messages.success(request, "Книга успешно возвращена. Спасибо!")
    else:
        messages.info(request, "Эту книгу вернуть нельзя, бронирование уже закрыто.")
    return redirect("user_reservations")
