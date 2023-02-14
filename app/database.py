import databases
import sqlalchemy
import ormar
from app.core.config import settings
from pydantic import EmailStr
from ormar import DateTime
from datetime import datetime

database = databases.Database(settings.DATABASE_URI)
metadata = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(settings.DATABASE_URI)


class User(ormar.Model):
    class Meta:
        database = database
        metadata = metadata

    id: int = ormar.Integer(primary_key=True)
    username: str = ormar.String(max_length=100)
    email: EmailStr = ormar.String(max_length=100, unique=True)
    active: bool = ormar.Boolean(default=True)
    hashed_password: str = ormar.String(max_length=64)
    is_repro_admin: bool = ormar.Boolean(default=False)
    credits: int = ormar.Integer(default=0)
    created_at: DateTime = ormar.DateTime(default=datetime.now)


class File(ormar.Model):
    class Meta:
        database = database
        metadata = metadata

    id: int = ormar.Integer(primary_key=True)
    file_name: str = ormar.String(max_length=100)
    file: str = ormar.LargeBinary(max_length=10000000, represent_as_base64_str=True)
    page_count: int = ormar.Integer()
    user: User = ormar.ForeignKey(User)
    created_at: DateTime = ormar.DateTime(default=datetime.now)


# class Order(ormar.Model):
#     class Meta:
#         database = database
#         metadata = metadata
#
#     id: int = ormar.Integer(primary_key=True)
#     user: str = ormar.ForeignKey(User)
#     repro: User | None = ormar.ForeignKey(User)
#     created_at: DateTime = ormar.DateTime(default=datetime.now)
#     payment_completed: bool = ormar.Boolean(default=True)

# class OrderFile(ormar.Model):
#     class Meta:
#         database = database
#         metadata = metadata
#
#     id: int = ormar.Integer(primary_key=True)
#     files:


metadata.create_all(engine)


