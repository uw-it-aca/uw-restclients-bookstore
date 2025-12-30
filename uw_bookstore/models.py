# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from datetime import timezone
import json
from restclients_core import models
from restclients_core.models import Model
from dateutil.parser import parse


class Textbook(Model):
    course_id = models.CharField(max_length=50, null=True)
    search_url = models.CharField(max_length=255, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.books = []

    def json_data(self):
        book_json_data = []
        for book in self.books:
            book_json_data.append(book.json_data())
        return {
            "course_id": self.course_id,
            "search_url": self.search_url,
            "books": book_json_data}

    def __str__(self):
        return json.dumps(self.json_data())


class Book(Model):
    isbn = models.CharField(max_length=20)
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    lowest_price = models.DecimalField(max_digits=7, decimal_places=2)
    highest_price = models.DecimalField(max_digits=7, decimal_places=2)
    used_price = models.DecimalField(max_digits=7, decimal_places=2)
    is_required = models.NullBooleanField()
    notes = models.TextField()
    cover_image_url = models.CharField(max_length=2048)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.authors = []

    def json_data(self):
        data = {
            'isbn': self.isbn,
            'title': self.title,
            'authors': [],
            'price': self.price,
            'used_price': self.used_price,
            'lowest_price': self.lowest_price,
            'highest_price': self.highest_price,
            'is_required': self.is_required,
            'notes': self.notes,
            'cover_image_url': self.cover_image_url,
        }

        for author in self.authors:
            data["authors"].append(author.json_data())
        return data

    def __str__(self):
        return json.dumps(self.json_data())


class BookAuthor(Model):
    name = models.CharField(max_length=255)

    def json_data(self):
        data = {'name': self.name}
        return data


class DigitalItems(Model):
    isbn = models.CharField(max_length=20)
    bookstore_item_id = models.PositiveIntegerField()
    opt_out_status = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data")
        if data is None:
            return super(DigitalItems, self).__init__(*args, **kwargs)
        self.isbn = data.get("ISBN")
        self.bookstore_item_id = data.get("ItemInternalID")
        self.opt_out_status = data.get("OptsOutStatus")
        self.paid = data.get("Paid")
        self.price = data.get("Price")

    def json_data(self):
        return {
            'isbn': self.isbn,
            'bookstore_item_id': self.bookstore_item_id,
            'opt_out_status': self.opt_out_status,
            'paid': self.paid,
            'price': self.price
        }

    def __str__(self):
        return json.dumps(self.json_data())


class IACourse(Model):
    sln = models.PositiveIntegerField()
    bookstore_course_id = models.PositiveIntegerField()

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data")
        if data is None:
            return super(IACourse, self).__init__(*args, **kwargs)
        self.sln = data.get("SLN")
        self.bookstore_course_id = data.get("BookstoreCourseID")
        self.digital_items = {}
        dis = data.get("DigitalItems")
        if dis and len(dis):
            for di in dis:
                dm = DigitalItems(data=di)
                if dm:
                    self.digital_items[dm.isbn] = dm

    def json_data(self):
        data = {
            'sln': self.sln,
            'bookstore_course_id': self.bookstore_course_id,
            'digital_items': {}
        }
        for di in self.digital_items.values():
            data['digital_items'][di.isbn] = di.json_data()
        return data

    def __str__(self):
        return json.dumps(self.json_data())


class TermIACourse(Model):
    quarter = models.CharField(max_length=6)
    year = models.PositiveSmallIntegerField()
    balance = models.DecimalField(max_digits=7, decimal_places=2)
    payment_due_day = models.DateTimeField()
    bookstore_digital_material_url = models.CharField(max_length=255)
    bookstore_checkout_url = models.CharField(max_length=255)
    last_updated = models.DateTimeField()

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data")
        if data is None:
            return super(TermIACourse, self).__init__(*args, **kwargs)

        self.year = data.get("Year")
        self.quarter = data.get("Quarter")
        self.balance = data.get("BalanceToPay")
        self.payment_due_day = str_to_datetime(data.get("PaymentDeadline"))
        self.bookstore_digital_material_url = (
            data.get("BookstoreDigitalMaterialLink"))
        self.bookstore_checkout_url = data.get("BookstoreCheckOutLink")
        self.last_updated = str_to_datetime(data.get("LastUpdated"))
        self.ia_courses = {}
        iacs = data.get("IACourses")
        if iacs and len(iacs):
            for aic in iacs:
                iac = IACourse(data=aic)
                if iac:
                    self.ia_courses[iac.sln] = iac

    def json_data(self):
        data = {
            'quarter': self.quarter,
            'year': self.year,
            'balance': self.balance,
            'payment_due_day': date_to_str(self.payment_due_day),
            'bookstore_digital_material_url': (
                self.bookstore_digital_material_url),
            'bookstore_checkout_url': self.bookstore_checkout_url,
            'last_updated': date_to_str(self.last_updated),
            'ia_courses': {}
        }
        for iac in self.ia_courses.values():
            data['ia_courses'][iac.sln] = iac.json_data()
        return data

    def __str__(self):
        return json.dumps(self.json_data())


def str_to_datetime(s):
    # Returns UTC-normalized datetime object
    if (s and len(s)):
        dt = parse(s)
        # Only second precision is needed.
        # The microseconds are discarded as JS can't handle it.
        dt = dt.replace(microsecond=0)
        return dt.astimezone(timezone.utc)
    return None


def date_to_str(dt):
    # datetime.datetime.isoformat
    return dt.isoformat() if dt else None
