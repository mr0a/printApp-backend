import databases
import sqlalchemy
import ormar
from app.core.config import settings
from pydantic import EmailStr
from ormar import DateTime
from typing import Optional
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
    credits: int = ormar.Integer(default=0)
    created_at: datetime = ormar.DateTime(
        server_default=sqlalchemy.func.now()
    )


class File(ormar.Model):
    class Meta:
        database = database
        metadata = metadata

    id: int = ormar.Integer(primary_key=True)
    file_name: str = ormar.String(max_length=100)
    file: str = ormar.LargeBinary(max_length=10000000, represent_as_base64_str=True)
    size: int = ormar.Integer()
    page_count: int = ormar.Integer()
    owner: User = ormar.ForeignKey(User)
    created_at: datetime = ormar.DateTime(
        server_default=sqlalchemy.func.now()
    )


class Repro(ormar.Model):
    class Meta:
        database = database
        metadata = metadata
    
    id: int = ormar.Integer(primary_key=True)
    username: str = ormar.String(max_length=30)
    email: EmailStr = ormar.String(max_length=100)
    hashed_password: str = ormar.String(max_length=64)
    created_at: datetime = ormar.DateTime(
        server_default=sqlalchemy.func.now()
    )


class FileConfig(ormar.Model):
    class Meta:
        database = database
        metadata = metadata
    
    id: int = ormar.Integer(primary_key=True)
    sheet_size: str = ormar.String(max_length=2)
    copies: int = ormar.SmallInteger(default=1)
    page_selection: str = ormar.String(max_length=20)


# class OrderFile(ormar.Model):
#     class Meta:
#         database = database
#         metadata = metadata

#     id: int = ormar.Integer(primary_key=True)
#     files: Optional[list[File]] = ormar.ManyToMany(File, through=FileConfig)
#     is_grayscale: bool = ormar.Boolean(default=True)


class Order(ormar.Model):
    class Meta:
        database = database
        metadata = metadata

    id: int = ormar.Integer(primary_key=True)
    user: User = ormar.ForeignKey(User)
    repro: Optional[Repro] = ormar.ForeignKey(Repro)
    created_at: datetime = ormar.DateTime(
        server_default=sqlalchemy.func.now()
    )
    total_amount: int = ormar.Integer()
    is_paid: bool = ormar.Boolean(default=False)
    payment_method: str = ormar.String(max_length=50)
    transaction_id: int = ormar.Integer(nullable=True)
    status: str = ormar.String(max_length=20, default="DRAFT")
    updated_at: datetime = ormar.DateTime(server_default=sqlalchemy.func.now())
    # order_files: Optional[list[FileConfig]] = ormar.ForeignKey(FileConfig, virtual=True)
    files = ormar.ManyToMany(File, through=FileConfig)


metadata.create_all(engine)


