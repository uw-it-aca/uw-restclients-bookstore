# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import mock
from unittest import skipIf, TestCase
from restclients_core.exceptions import DataFailureException
from uw_bookstore import Bookstore
from uw_bookstore.models import Textbook
from uw_bookstore.util import fdao_bookstore_override


@fdao_bookstore_override
class BookstoreTest(TestCase):

    def test_get_bookby_quarter_sln(self):
        books = Bookstore()
        # self.maxDiff = None
        result = books.get_books_by_quarter_sln("spring", 13833)
        self.assertEqual(
            result.json_data(),
            {
                "course_id": None,
                "search_url": None,
                "books": []
            },
        )
        self.assertIsNotNone(str(result))
        result = books.get_books_by_quarter_sln('autumn', 10001)
        self.assertEqual(
            result.json_data(),
            {"course_id": None, "search_url": None, "books": []})
        self.assertRaises(
            DataFailureException,
            books.get_books_by_quarter_sln, "autumn", 10000
        )
        self.assertRaises(
            DataFailureException,
            books.get_books_by_quarter_sln, "autumn", 10009
        )

        result = books.get_books_by_quarter_sln("spring", 13830)
        self.assertTrue(isinstance(result, Textbook))
        self.assertIsNotNone(result.books)
        self.assertEqual(len(result.books), 2)
        self.assertEqual(result.books[0].isbn, "9780878935970")
        self.assertEqual(result.course_id, "uws-phys-111-a-123")
        self.assertEqual(
            result.search_url,
            "https://ubookstore.com/pages/adoption-search/course="
        )
        self.assertIsNotNone(str(result.books[0]))
        jdata = result.json_data()
        self.assertTrue("books" in jdata)
        self.assertTrue(len(jdata["books"]) == 2)
        self.assertTrue("course_id" in jdata)
        self.assertTrue("search_url" in jdata)

        result = books.get_books_by_quarter_sln("autumn", 19187)
        self.assertTrue(isinstance(result, Textbook))
        self.assertIsNotNone(result.books)
        self.assertEqual(len(result.books), 2)
        self.assertEqual(len(result.books[0].authors), 2)
        self.assertEqual(result.books[0].authors[0].name, "Groom1")
        self.assertEqual(result.books[0].authors[1].name, "Groom2")

    def test_get_books(self):
        books = Bookstore()
        sln_books = books.get_textbooks("spring", {13830, 13833})
        self.assertEqual(len(sln_books), 2)
        self.assertEqual(len(sln_books[13833].books), 0)
        self.assertEqual(len(sln_books[13830].books), 2)

        sln_books = books.get_textbooks("autumn", {10000, 19187})
        self.assertEqual(len(sln_books), 2)
        self.assertTrue(isinstance(sln_books[10000], DataFailureException))
        self.assertTrue(isinstance(sln_books[19187], Textbook))

        self.assertEqual(books.get_textbooks(None, None), {})
