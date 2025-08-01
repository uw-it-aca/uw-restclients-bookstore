# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
This is the interface for interacting with the UW Bookstore's book service.
"""

import json
import logging
from uw_bookstore import DAO, Bookstore
from uw_bookstore.models import TermIACourse
from restclients_core.exceptions import DataFailureException

API_ENDPOINT = "/uw/iacourse_status.json?regid="
logger = logging.getLogger(__name__)


class IACoursesStatus(Bookstore):

    def get_iacourse_status(self, regid):
        url = f"{API_ENDPOINT}{regid}"
        resp_json = self.get_url(url)

        terms_iacourses = {}
        if len(resp_json):
            for item in resp_json:
                tiac = TermIACourse(data=item)
                if tiac:
                    terms_iacourses[
                        "{}{}".format(tiac.quarter, tiac.year)] = tiac
        return terms_iacourses
