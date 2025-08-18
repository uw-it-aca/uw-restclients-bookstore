# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


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

    def get_url(self, url):
        """
        url: str -> json-data
        Raise DataFailureException
        """
        response = DAO.getURL(url, {"Accept": "application/json"})
        if response.status != 200:
            logger.error(f"{url} => {response.status} => {response.data}")
            raise DataFailureException(url, response.status, response.data)

        try:
            return json.loads(response.data)
        except Exception as ex:
            logger.error(f"{url} => {ex} ==> {response.data}")
            raise DataFailureException(
                url, 200, f"InvalidData: {ex} {response.data[:100]}")

    def get_books_by_quarter_sln(self, quarter, sln):
        """
        quarter: str, sln: str -> Textbook
        Raise DataFailureException
        """
        url = f"{API_ENDPOINT}?quarter={quarter}&sln1={sln}&returnlink=t"
        data = self.get_url(url)
        books = []
        value = data.get(str(sln), [])
        if value and isinstance(value, list):
            for book_data in value:
                book = Book(
                    isbn=book_data.get("isbn"),
                    title=book_data.get("title"),
                    price=book_data.get("price"),
                    lowest_price=book_data.get("lowest_price"),
                    highest_price=book_data.get("highest_price"),
                    used_price=book_data.get("used_price"),
                    is_required=book_data.get("required"),
                    notes=book_data.get("notes"),
                    cover_image_url=book_data.get("cover_image"),
                )
                book.authors = [
                    BookAuthor(name=a.get("name"))
                    for a in book_data.get("authors", [])
                    if a.get("name")
                ]
                books.append(book)
        link = data.get("ubsLink", {})
        textbook = Textbook(
            course_id=link.get("course_id"),
            search_url=link.get("search")
        )
        textbook.books = books
        logger.debug(f"get_books {url} ==> {str(textbook)}")
        return textbook

    def get_textbooks(self, quarter, sln_set):
        """
        Get textbook requirements for course SLNs.
        quarter: str, sln_set: Set[str])
        Returns a Dict[sln str, Union[Textbook, DataFailureException]]
        """
        if not quarter or not sln_set:
            return {}
        logger.debug(f"get_textbooks for {quarter} {sln_set}")
        max_workers = min(len(sln_set), 13)
        books = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            task_to_sln = {
                executor.submit(
                    self.get_books_by_quarter_sln, quarter, sln): sln
                for sln in sln_set
            }

            for task in as_completed(task_to_sln):
                sln = task_to_sln[task]
                try:
                    books[sln] = task.result()
                    logger.debug(f"Task for {sln} ==> {books[sln]}")
                except Exception as ex:
                    books[sln] = ex
                    logger.debug(f"Task for {sln} failed: {ex}")
                    # Pass up the error but not raise excetion
        return books
