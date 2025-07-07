# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import mock
from unittest import TestCase
from uw_bookstore.digital_material import IACoursesStatus
from restclients_core.exceptions import DataFailureException
from uw_bookstore.util import fdao_bookstore_override


@fdao_bookstore_override
class IACoursesStatusTest(TestCase):
    def test_get(self):
        ias = IACoursesStatus()
        result = ias.get_iacourse_status('12345678901234567890123456789012')
        self.assertEqual(len(result.keys()), 2)
        tiacs = result.get("spring2013")
        self.maxDiff = None
        self.assertIsNotNone(tiacs.json_data())
        self.assertIsNotNone(str(tiacs))
        self.assertEqual(tiacs.balance, 219.85)
        self.assertTrue(len(tiacs.bookstore_checkout_url) > 0)
        self.assertTrue(len(tiacs.bookstore_digital_material_url) > 0)
        self.assertIsNotNone(tiacs.payment_due_day)
        self.assertIsNotNone(tiacs.ia_courses)
        self.assertEqual(len(tiacs.ia_courses.keys()), 4)
        self.assertEqual(
            tiacs.ia_courses[13830].json_data(),
            {
                'sln': 13830,
                'bookstore_course_id': 1000157,
                'digital_items': {
                    '9781256396362': {
                        'bookstore_item_id': 2000268,
                        'isbn': '9781256396362',
                        'opt_out_status': False,
                        'paid': False,
                        'price': 24.26
                    }
                }
            }
        )
        self.assertEqual(tiacs.ia_courses[11646].digital_items, {})
        self.assertIsNotNone(str(tiacs.ia_courses[13833]))
        self.assertIsNotNone(
            str(tiacs.ia_courses[13833].digital_items['9781256396362']))

        tiacs1 = result.get("summer2013")
        self.assertEqual(tiacs1.balance, 99.00)

        self.assertRaises(
            DataFailureException, ias.get_iacourse_status, '00000')
