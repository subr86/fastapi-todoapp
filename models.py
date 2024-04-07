from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(length=100), unique=True)
    username = Column(String(length=100), unique=True)
    first_name = Column(String(length=100))
    last_name = Column(String(length=100))
    password = Column(String(length=256))
    is_active = Column(Boolean, default=True)
    role = Column(String(length=100))
    phone_number = Column(String(length=100), default=None)


class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(length=100))
    description = Column(String(length=100))
    priority = Column(Integer)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
