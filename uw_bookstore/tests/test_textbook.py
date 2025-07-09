# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import mock
from unittest import skipIf, TestCase
from uw_bookstore import Bookstore
from restclients_core.exceptions import DataFailureException
from uw_bookstore.util import fdao_bookstore_override


@fdao_bookstore_override
class BookstoreTest(TestCase):

    def test_get_bookby_quarter_sln(self):
        books = Bookstore()

        result = books.get_books_by_quarter_sln('autumn', 19187)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].isbn, '9780878935970')

        with self.assertRaises(DataFailureException):
            books.get_books_by_quarter_sln('autumn', 00000)
        with self.assertRaises(DataFailureException):
            books.get_books_by_quarter_sln('autumn', 0)
        with self.assertRaises(DataFailureException):
            books.get_books_by_quarter_sln('autumn', 10000)
        self.assertEqual(
            books.get_books_by_quarter_sln("autumn", 10001), [])

    def test_get_books(self):
        books = Bookstore()
        sln_books = books.get_textbooks("spring", {13830, 13833})
        self.assertEqual(len(sln_books), 2)
        self.assertEqual(len(sln_books[13833]), 0)
        self.assertEqual(len(sln_books[13830]), 2)

        with self.assertRaises(DataFailureException):
            books.get_textbooks("autumn", {10000, 19187})

        self.assertIsNone(books.get_textbooks(None, None))

    def test_verba_link(self):
        books = Bookstore()
        verba_link = books.get_order_url("spring", {13830, 13833})

        self.assertEqual(
            ('http://www.ubookstore.com/adoption-search-results?' +
             'ccid=9335,10822'),
            verba_link)

        with self.assertRaises(DataFailureException):
            books.get_textbooks("autumn", {10002, 19187})
