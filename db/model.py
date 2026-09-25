# Import necessary modules from SQLAlchemy
from datetime import datetime, timezone

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Base class
class Base(DeclarativeBase):
    pass

# Player model
class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    osu_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)

# Mapper model
class Mapper(Base):
    __tablename__ = "mappers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    osu_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)

class LastChecked(Base):
    __tablename__ = "last_checked"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    last_checked: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False,
    )