from restclients_core.util.decorators import use_mock
from uw_bookstore import Bookstore_DAO

fdao_bookstore_override = use_mock(Bookstore_DAO())
