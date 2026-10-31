from sqladmin import ModelView
from src.auth.models import User

class UserAdmin(ModelView, model=User):
    name="User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    column_list = [User.id, User.email, User.role, User.is_active, User.created_at]
    column_searchable_list = [User.email]
    column_sortable_list = [User.id, User.created_at]
    form_excluded_columns = [User.hashed_password, User.created_at, User.updated_at]