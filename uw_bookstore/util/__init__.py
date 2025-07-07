# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from restclients_core.util.decorators import use_mock
from uw_bookstore import Bookstore_DAO

fdao_bookstore_override = use_mock(Bookstore_DAO())
