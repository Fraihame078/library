"""
Модели для приложения библиотеки.

В этой небольшой учебной работе хранятся данные о книгах и действиях
пользователей (бронирования и покупки).  Код написан достаточно
просто, чтобы было понятно начинающему разработчику.
"""

from django.conf import settings
from django.db import models


class Book(models.Model):
    """Модель книги, доступной в библиотеке."""

    title = models.CharField(max_length=200, help_text="Название книги")
    author = models.CharField(max_length=200, help_text="Автор")
    description = models.TextField(blank=True, help_text="Описание")
    cover_image = models.ImageField(
        upload_to="book_covers/",
        blank=True,
        null=True,
        help_text="Обложка книги",
    )
    available_copies = models.PositiveIntegerField(
        default=1, help_text="Количество доступных экземпляров"
    )

    # Флаг VIP: книги с VIP пометкой нельзя бронировать, их можно только купить.
    is_vip = models.BooleanField(
        default=False,
        help_text="Эта книга относится к VIP‑разделу (только покупка)",
    )
    # Цена для VIP книг.  Для обычных книг это поле можно оставить пустым.
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Цена книги (если книга VIP)",
    )

    class Meta:
        ordering = ["title"]
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def __str__(self) -> str:
        return self.title

    def is_available(self) -> bool:
        """Return True if at least one copy is available."""
        return self.available_copies > 0


class Reservation(models.Model):
    """Represents a reservation of a book by a user."""

    STATUS_CHOICES = [
        ("reserved", "Зарезервировано"),
        ("returned", "Возвращено"),
        ("cancelled", "Отменено"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations",
        verbose_name="Пользователь",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="reservations",
        verbose_name="Книга",
    )
    reserved_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата бронирования"
    )
    return_date = models.DateField(
        null=True, blank=True, verbose_name="Дата возврата"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="reserved",
        verbose_name="Статус",
    )

    class Meta:
        ordering = ["-reserved_at"]
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

    def __str__(self) -> str:
        return f"{self.book.title} – {self.user.username}"


class Purchase(models.Model):
    """Represents the purchase of a VIP book by a user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="purchases",
        verbose_name="Пользователь",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="purchases",
        verbose_name="Книга",
    )
    purchased_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата покупки"
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Цена",
    )

    class Meta:
        ordering = ["-purchased_at"]
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки"

    def __str__(self) -> str:
        return f"{self.book.title} – {self.user.username} (покупка)"
