from starlette_admin.contrib.sqla import Admin, ModelView
from starlette_admin.fields import (
    StringField, EmailField, FloatField, BooleanField, DateTimeField, PasswordField
)
from starlette.requests import Request
from starlette_admin.exceptions import FormValidationError
from sqlalchemy.orm import Session

from database import engine
from models import Post, BaseUser
from passlib.hash import bcrypt


admin = Admin(engine, title="Example: SQLAlchemy")

admin.add_view(ModelView(Post))

class UserAdmin(ModelView):
    # 1) Управляем набором полей и их отображением
    fields = [
        "id",
        EmailField("email", label="E-mail", required=True, help_text="уникальный e-mail"),
        BooleanField("email_is_verified", label="E-mail подтверждён", read_only=True),
        StringField("username", label="Username"),
        # «виртуальное» поле для ввода пароля в форме (не из модели)
        PasswordField("password", label="Пароль", exclude_from_list=True, exclude_from_detail=True),
        BooleanField("is_active", label="Активен"),
        BooleanField("is_deleted", label="Удалён"),
        DateTimeField("last_login", label="Последний вход", read_only=True),
        DateTimeField("created_at", label="Создан", read_only=True),
    ]

    # 2) Что скрывать на разных экранах
    exclude_fields_from_list = ["hashed_password", "password"]          # в таблице
    exclude_fields_from_detail = ["hashed_password", "password"]        # на карточке
    exclude_fields_from_create = ["id", "email_is_verified", "last_login", "created_at", "hashed_password"]
    exclude_fields_from_edit = ["id", "email_is_verified", "last_login", "created_at", "hashed_password"]

    # 3) Поиск/сортировка
    searchable_fields = ["email", "username"]      # поисковая строка
    sortable_fields = ["id", "email", "username", "created_at", "last_login"]
    fields_default_sort = [("created_at", True)]         # True = по убыванию

    # 4) Значения по умолчанию и пред/пост-обработчики
    async def before_create(self, request: Request, data: dict, obj: BaseUser):
        """
        Здесь самое удобное место, чтобы проставить дефолты и обработать виртуальные поля.
        """
        # булевые флаги по умолчанию
        data.setdefault("marketing_opt_in", False)
        data.setdefault("is_active", True)
        data.setdefault("is_deleted", False)
        data.setdefault("email_is_verified", False)

        # обработка виртуального поля password -> hashed_password
        raw = data.pop("password", None)
        if raw:
            data["hashed_password"] = bcrypt.hash(raw)

        email = data.get("email")
        username = data.get("username")

        errors = {}
        if email:
            with Session(engine) as session:
                if session.query(BaseUser).filter_by(email=email).first():
                    errors["email"] = "Такой email уже существует"

        if username:
            with Session(engine) as session:
                if session.query(BaseUser).filter_by(username=username).first():
                    errors["username"] = "Такой username уже существует"

        if errors:
            raise FormValidationError(errors)

        return await super().before_create(request, data, obj)


    async def before_edit(self, request: Request, data: dict, obj: BaseUser):
        """
        Аналогично для обновления: если ввели новый пароль — перехешируем.
        """
        raw = data.pop("password", None)
        if raw:
            data["hashed_password"] = bcrypt.hash(raw)
        # запрещаем править email_is_verified напрямую (он read_only, но на всякий случай)
        data.pop("email_is_verified", None)
        return await super().before_edit(request, data, obj)

admin.add_view(UserAdmin(BaseUser, label="Пользователи", icon="fa fa-user"))