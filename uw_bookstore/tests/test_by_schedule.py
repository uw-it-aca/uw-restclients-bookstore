import logging
from unittest import skipIf, TestCase
from uw_bookstore import Bookstore
from uw_sws.term import get_current_term,\
    get_term_by_year_and_quarter
from uw_sws.registration import get_schedule_by_regid_and_term
from restclients_core.exceptions import DataFailureException
from uw_bookstore.util import fdao_bookstore_override
from uw_sws.util import fdao_sws_override


@fdao_bookstore_override
@fdao_sws_override
class BookstoreScheduleTest(TestCase):
    def test_get_book(self):
        books = Bookstore()

        result = books.get_books_by_quarter_sln('autumn', 19187)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].isbn, '9780878935970')

        with self.assertRaises(DataFailureException):
            books.get_books_by_quarter_sln('autumn', 00000)
        with self.assertRaises(DataFailureException):
            books.get_books_by_quarter_sln('autumn', 0)

    def test_get_books_by_schedule(self):
        books = Bookstore()
        term = get_current_term()
        schedule = get_schedule_by_regid_and_term(
            'AA36CCB8F66711D5BE060004AC494FFE', term)
        schedule_books = books.get_books_for_schedule(schedule)

        self.assertEquals(len(schedule_books), 2)
        self.assertEqual(len(schedule_books[13833]), 0)
        self.assertEqual(len(schedule_books[13830]), 2)

        books = Bookstore()
        term = get_term_by_year_and_quarter(2013, 'winter')
        schedule = get_schedule_by_regid_and_term(
            'FE36CCB8F66711D5BE060004AC494F31', term,
            transcriptable_course="all")
        self.assertEquals(len(schedule.sections), 1)
        schedule_books = books.get_books_for_schedule(schedule)
        self.assertEquals(len(schedule_books), 0)

    def test_verba_link(self):
        books = Bookstore()

        term = get_current_term()
        schedule = get_schedule_by_regid_and_term(
            'AA36CCB8F66711D5BE060004AC494FFE', term)

        verba_link = books.get_url_for_schedule(schedule)

        self.assertEquals(
            ('http://www.ubookstore.com/adoption-search-results?' +
             'ccid=9335,10822'),
            verba_link)

        # no valid sln
        books = Bookstore()
        term = get_term_by_year_and_quarter(2013, 'winter')
        schedule = get_schedule_by_regid_and_term(
            'FE36CCB8F66711D5BE060004AC494F31', term,
            transcriptable_course="all")
        self.assertEqual(schedule.sections[0].sln, 0)
        self.assertIsNone(books.get_url_for_schedule(schedule))

    def test_dupe_slns(self):
        books = Bookstore()
        term = get_current_term()
        schedule = get_schedule_by_regid_and_term(
            'AA36CCB8F66711D5BE060004AC494FFE', term)

        schedule.sections.append(schedule.sections[0])
        schedule.sections.append(schedule.sections[0])
        schedule.sections.append(schedule.sections[0])
        schedule.sections.append(schedule.sections[0])
        schedule.sections.append(schedule.sections[0])

        verba_link = books.get_url_for_schedule(schedule)

        self.assertEquals(
            verba_link,
            'http://www.ubookstore.com/adoption-search-results' +
            '?ccid=9335,10822')

        schedule_books = books.get_books_for_schedule(schedule)
        self.assertEquals(len(schedule_books), 2)
