"""
Настройка административной панели для приложения библиотеки.

Здесь регистрируются модели в админке Django и настраиваются поля,
которые удобно видеть в таблицах.  Это стандартный способ настроить
отображение данных для администратора.
"""

from django.contrib import admin

from .models import Book, Reservation
from .models import Purchase


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Customise the admin list display for books."""

    list_display = (
        "title",
        "author",
        "available_copies",
        "is_vip",
        "price",
    )
    list_filter = ("author", "is_vip")
    search_fields = ("title", "author")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """Admin view for reservations with useful filters and search."""

    list_display = ("book", "user", "status", "reserved_at", "return_date")
    list_filter = ("status", "reserved_at")
    search_fields = ("book__title", "user__username")
    raw_id_fields = ("book", "user")


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    """Admin view for purchases."""

    list_display = ("book", "user", "price", "purchased_at")
    list_filter = ("purchased_at",)
    search_fields = ("book__title", "user__username")
