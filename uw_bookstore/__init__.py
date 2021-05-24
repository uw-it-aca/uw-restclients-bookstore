# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
This is the interface for interacting with the UW Bookstore's book service.
"""

from uw_bookstore.dao import Bookstore_DAO
from restclients_core.exceptions import DataFailureException
from uw_bookstore.models import Book, BookAuthor
from concurrent.futures import ThreadPoolExecutor
import json
import re


BOOK_PREFIX = "http://uw-seattle.verbacompare.com/m?section_id="
API_ENDPOINT = "/uw/json_utf8_202007.ubs"
DAO = Bookstore_DAO()


class Bookstore(object):
    """
    Get book information for courses.
    """

    def get_books_by_quarter_sln(self, quarter, sln):
        url = API_ENDPOINT + "?quarter=%s&%s&returnlink=t" % (
            quarter,
            self._get_sln_string(sln),
            )
        response = DAO.getURL(url, {"Accept": "application/json"})
        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)

        books = []

        sln_data = data[str(sln)]

        if len(sln_data):
            for book_data in sln_data:
                book = Book()
                book.isbn = book_data["isbn"]
                book.title = book_data["title"]
                book.price = book_data["price"]
                book.lowest_price = book_data["lowest_price"]
                book.highest_price = book_data["highest_price"]
                book.used_price = book_data["used_price"]
                book.is_required = book_data["required"]
                book.notes = book_data["notes"]
                book.cover_image_url = book_data["cover_image"]
                book.authors = []

                for author_data in book_data["authors"]:
                    author = BookAuthor()
                    author.name = author_data["name"]
                    book.authors.append(author)

                    books.append(book)
        return books

    def get_books_for_schedule(self, schedule):
        """
        Returns a dictionary of data.  SLNs are the keys, an array of Book
        objects are the values.
        """
        slns = self._get_slns(schedule)

        books = {}

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(
                    self.get_books_by_quarter_sln,
                    [schedule.term.quarter] * len(slns),
                    slns
                    )
            executor.shutdown(wait=True)

        for result, sln in zip(results, slns):
            books[sln] = result

        return books

    def get_url_for_schedule(self, schedule):
        """
        Returns a link to verba.  The link varies by campus and schedule.
        Multiple calls to this with the same schedule may result in
        different urls.
        """
        url = self._get_url(schedule)
        if url is None:
            return None
        response = DAO.getURL(url, {"Accept": "application/json"})
        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)

        if "ubsLink" in data:
            return data["ubsLink"][0]["search"]

    def _get_url(self, schedule):
        sln_string = self._get_slns_string(schedule)
        if sln_string:
            url = API_ENDPOINT + "?quarter=%s&%s&returnlink=t" % (
                schedule.term.quarter,
                sln_string,
            )
            return url
        return None

    def _get_sln_string(self, sln):
        return "sln1=%d" % sln

    def _get_slns(self, schedule):
        slns = []
        for section in schedule.sections:
            sln = section.sln
            if sln and sln not in slns:
                slns.append(sln)
        return slns

    def _get_slns_string(self, schedule):
        valid_slns = self._get_slns(schedule)
        if len(valid_slns):
            slns = []
            sln_count = 1
            for sln in valid_slns:
                slns.append("sln%d=%d" % (sln_count, sln))
                sln_count += 1
            sln_string = "&".join(slns)
            return sln_string
        return None
