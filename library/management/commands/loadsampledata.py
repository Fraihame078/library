"""
Команда для загрузки примерочных данных в базу.

Эта команда добавляет несколько книг, чтобы библиотека не была пустой.
Она проверяет, есть ли книга с таким названием, и не создаёт
дубликаты.  Обложки берутся из каталога ``media/book_covers``.  Часть
книг помечена как VIP (их можно только купить).
"""

import os

from django.core.files import File
from django.core.management.base import BaseCommand
from django.conf import settings

from library.models import Book


class Command(BaseCommand):
    help = "Load sample books with covers and descriptions"

    def handle(self, *args, **options):  # type: ignore[override]
        # Define sample book data.  Each entry corresponds to a Book
        # instance.  The 'cover' points to a PNG file in
        # settings.MEDIA_ROOT / 'book_covers'.
        books = [
            {
                "title": "Война и мир",
                "author": "Лев Толстой",
                "description": "Эпический роман о судьбах людей на фоне Отечественной войны 1812 года.",
                "cover": "cover1.png",
                "available_copies": 3,
                "is_vip": False,
            },
            {
                "title": "Мастер и Маргарита",
                "author": "Михаил Булгаков",
                "description": "Мистический роман о посещении Москвы дьяволом и истории любви мастера и Маргариты.",
                "cover": "cover3.png",
                "available_copies": 4,
                "is_vip": False,
            },
            {
                "title": "Преступление и наказание",
                "author": "Фёдор Достоевский",
                "description": "История о бедном студенте, который совершает убийство и мучается совестью.",
                "cover": "cover2.png",
                "available_copies": 2,
                "is_vip": False,
            },
            {
                "title": "Анна Каренина",
                "author": "Лев Толстой",
                "description": "Трагическая история любви Анны Карениной и Алексея Вронского.",
                "cover": "cover4.png",
                "available_copies": 3,
                "is_vip": False,
            },
            {
                "title": "Отцы и дети",
                "author": "Иван Тургенев",
                "description": "Повесть о противостоянии поколений и нигилизме.",
                "cover": "cover5.png",
                "available_copies": 2,
                "is_vip": False,
            },
            {
                "title": "Евгений Онегин",
                "author": "Александр Пушкин",
                "description": "Роман в стихах о молодом дворянине и его отношении к жизни и любви.",
                "cover": "cover1.png",
                "available_copies": 3,
                "is_vip": False,
            },
            {
                "title": "Обломов",
                "author": "Иван Гончаров",
                "description": "Роман о дворянине, погружённом в лень и апатию, и его друге Штольце.",
                "cover": "cover2.png",
                "available_copies": 2,
                "is_vip": False,
            },
            {
                "title": "Доктор Живаго",
                "author": "Борис Пастернак",
                "description": "История врача и поэта Юрия Живаго на фоне революционных событий в России.",
                "cover": "cover3.png",
                "available_copies": 3,
                "is_vip": False,
            },
            {
                "title": "Тихий Дон",
                "author": "Михаил Шолохов",
                "description": "Эпопея о донских казаках в годы революции и гражданской войны.",
                "cover": "cover4.png",
                "available_copies": 4,
                "is_vip": False,
            },
            {
                "title": "Капитанская дочка",
                "author": "Александр Пушкин",
                "description": "Повесть о любви, чести и событиях восстания Пугачёва.",
                "cover": "cover5.png",
                "available_copies": 3,
                "is_vip": False,
            },
            # VIP books
            {
                "title": "1984",
                "author": "Джордж Оруэлл",
                "description": "Антиутопия о тоталитарном государстве и контроле над сознанием.",
                "cover": "cover1.png",
                "available_copies": 1,
                "is_vip": True,
                "price": 9.99,
            },
            {
                "title": "О дивный новый мир",
                "author": "Олдос Хаксли",
                "description": "Роман о технологически управляемом обществе будущего.",
                "cover": "cover2.png",
                "available_copies": 1,
                "is_vip": True,
                "price": 8.99,
            },
            {
                "title": "Великий Гэтсби",
                "author": "Фрэнсис Скотт Фицджеральд",
                "description": "История о богатстве, любви и утрате в эпоху джаза.",
                "cover": "cover3.png",
                "available_copies": 1,
                "is_vip": True,
                "price": 7.99,
            },
            {
                "title": "Гарри Поттер и философский камень",
                "author": "Дж. К. Роулинг",
                "description": "Первая книга о мальчике‑волшебнике, который узнаёт о своём предназначении.",
                "cover": "cover4.png",
                "available_copies": 1,
                "is_vip": True,
                "price": 10.99,
            },
            {
                "title": "Хоббит",
                "author": "Дж. Р. Р. Толкин",
                "description": "Приключенческий роман о путешествии Бильбо Бэггинса.",
                "cover": "cover5.png",
                "available_copies": 1,
                "is_vip": True,
                "price": 8.49,
            },
        ]

        created_count = 0
        for data in books:
            if Book.objects.filter(title=data["title"]).exists():
                self.stdout.write(
                    self.style.NOTICE(
                        f"Книга '{data['title']}' уже существует, пропускаем."
                    )
                )
                continue
            book = Book(
                title=data["title"],
                author=data["author"],
                description=data["description"],
                available_copies=data["available_copies"],
                is_vip=data["is_vip"],
                price=data.get("price"),
            )
            # Attach cover image if available
            cover_filename = data["cover"]
            media_path = os.path.join(settings.MEDIA_ROOT, "book_covers", cover_filename)
            if os.path.exists(media_path):
                with open(media_path, "rb") as f:
                    book.cover_image.save(cover_filename, File(f), save=False)
            book.save()
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f"Добавлена книга: {book.title}")
            )
        self.stdout.write(
            self.style.SUCCESS(f"Завершено. Добавлено {created_count} книг.")
        )