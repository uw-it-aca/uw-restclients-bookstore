# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
This is the interface for interacting with the UW Bookstore's book service.
"""

import logging
from uw_bookstore.dao import Bookstore_DAO
from restclients_core.exceptions import DataFailureException
from uw_bookstore.models import Book, BookAuthor, Textbook
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

logger = logging.getLogger(__name__)
API_ENDPOINT = "/uw/json_utf8_202507.ubs"
DAO = Bookstore_DAO()


class Bookstore(object):
    """
    Get book information for courses.
    """

    def get_books_by_quarter_sln(self, quarter, sln):
        url = f"{API_ENDPOINT}?quarter={quarter}&sln1={sln}&returnlink=t"
        logger.debug(f"get_books {url}")
        try:
            data = self.get_url(url)
        except Exception as ex:
            logger.error(f"{url}  {ex}")
            return ex
            # Pass up the error of individual sln book fetching

        return_val = Textbook()
        link = data.get("ubsLink", {})
        return_val.course_id = link.get("course_id")
        return_val.search_url = link.get("search")
        books = []
        value = data.get(str(sln), [])
        for book_data in value:
            book = Book()
            book.isbn = book_data.get("isbn")
            book.title = book_data.get("title")
            book.price = book_data.get("price")
            book.lowest_price = book_data.get("lowest_price")
            book.highest_price = book_data.get("highest_price")
            book.used_price = book_data.get("used_price")
            book.is_required = book_data.get("required")
            book.notes = book_data.get("notes")
            book.cover_image_url = book_data.get("cover_image")
            book.authors = []
            for author_data in book_data.get("authors"):
                author = BookAuthor()
                author.name = author_data.get("name")
                book.authors.append(author)
            logger.debug(f"get_books {url} ==> {str(book)}")
            books.append(book)
        return_val.books = books
        return return_val

    def get_url(self, url):
        response = DAO.getURL(url, {"Accept": "application/json"})
        logger.debug(f"{url} ==> {response.status} ==> {response.data}")
        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        try:
            return json.loads(response.data)
        except Exception as ex:
            logger.debug(f"{url} ==> {response.data} ==> {ex}")
            raise DataFailureException(
                url, 200, f"InvalidData: {ex} {response.data[:100]}")

    def get_textbooks(self, quarter, sln_set):
        """
        Returns a dictionary of sln to Textbook object or Exception object
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
                logger.debug(f"Task for {sln} returned {books[sln]}")

        return books
