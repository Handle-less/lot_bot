from .admin.handlers_dist import dp
from .admin.handlers_lots_add import dp
from .admin.handlers_lots_list import dp
from .admin.handlers_reports import dp
from .admin.handlers_user import dp
from .user.handlers_contacts import dp
from .user.handlers_lots import dp
from .user.handlers_verification import dp
from .commands import dp

__all__ = ["dp"]
