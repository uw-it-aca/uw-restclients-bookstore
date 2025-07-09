# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
This is the interface for interacting with the UW Bookstore's book service.
"""

import logging
from uw_bookstore.dao import Bookstore_DAO
from restclients_core.exceptions import DataFailureException
from uw_bookstore.models import Book, BookAuthor
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

logger = logging.getLogger(__name__)
API_ENDPOINT = "/uw/json_utf8_202007.ubs"
DAO = Bookstore_DAO()


class Bookstore(object):
    """
    Get book information for courses.
    """

    def get_textbooks(self, quarter, sln_set):
        """
        Returns a dictionary of sln to an array of Book objects.
        """
        if not quarter or not sln_set:
            return None
        books = {}
        logger.debug(f"get_textbooks for {quarter} {sln_set}")
        with ThreadPoolExecutor(max_workers=13) as executor:
            task_to_sln = {
                executor.submit(
                    self.get_books_by_quarter_sln, quarter, sln): sln
                for sln in sln_set
            }

            for task in as_completed(task_to_sln):
                sln = task_to_sln[task]
                books[sln] = task.result()
                logger.debug(f"Completed task for {sln}")
        return books

    def get_books_by_quarter_sln(self, quarter, sln):
        url = f"{API_ENDPOINT}?quarter={quarter}&sln1={sln}"
        logger.debug(f"get_books {url}")
        data = self.get_url(url)
        books = []
        value = data.get(str(sln))
        if value is None:
            return books
        for book_data in value:
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
            logger.debug(f"get_books {url} ==> {str(book)}")
            books.append(book)
        return books

    def get_order_url(self, quarter, sln_set):
        """
        Returns a dynamic link to verba.
        """
        sln_string = self._get_slns_string(sln_set)
        url = "{}?quarter={}&{}&returnlink=t".format(
            API_ENDPOINT, quarter, sln_string)
        logger.debug(f"get_order_url {quarter} {sln_set} {url}")
        data = self.get_url(url)

        if "ubsLink" in data:
            return data["ubsLink"][0]["search"]

    def _get_slns_string(self, sln_set):
        slns = []
        sln_count = 1
        for sln in sln_set:
            slns.append(f"sln{sln_count}={sln}")
            sln_count += 1
        sln_string = "&".join(slns)
        return sln_string

    def get_url(self, url):
        response = DAO.getURL(url, {"Accept": "application/json"})
        logger.debug(f"{url} ==> {response.status} ==> {response.data}")
        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        try:
            return json.loads(response.data)
        except Exception as ex:
            logger.error(f"{url} ==> {response.data} ==> {ex}")
            raise DataFailureException(
                url, response.status, {"exception": ex, "data": response.data}
            )
