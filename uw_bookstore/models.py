from restclients_core import models
from restclients_core.models import Model


class Book(Model):
    isbn = models.CharField(max_length=15)
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    used_price = models.DecimalField(max_digits=7, decimal_places=2)
    is_required = models.NullBooleanField()
    notes = models.TextField()
    cover_image_url = models.CharField(max_length=2048)

    def json_data(self):
        data = {
            'isbn': self.isbn,
            'title': self.title,
            'authors': [],
            'price': self.price,
            'used_price': self.used_price,
            'is_required': self.is_required,
            'notes': self.notes,
            'cover_image_url': self.cover_image_url,
        }

        for author in self.authors:
            data["authors"].append(author.json_data())
        return data


class BookAuthor(Model):
    name = models.CharField(max_length=255)

    def json_data(self):
        data = {'name': self.name}

        return data
