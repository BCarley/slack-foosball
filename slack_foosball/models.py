import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def generate_uuid():
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class Game(Base):
    __tablename__ = "games"

    id = mapped_column(String(36), index=True, primary_key=True, default=generate_uuid)
    red_attacker: Mapped[str] = mapped_column(String(30))
    red_defender: Mapped[str] = mapped_column(String(30))
    red_score: Mapped[int] = mapped_column(Integer())

    blue_attacker: Mapped[str] = mapped_column(String(30))
    blue_defender: Mapped[str] = mapped_column(String(30))
    blue_score: Mapped[int] = mapped_column(Integer())

    played_at: Mapped[datetime] = mapped_column(
        DateTime(), default=datetime.utcnow, index=True
    )
    submitted_by: Mapped[str] = mapped_column(String(30))

    def __repr__(self) -> str:
        return f"Game([{self.red_score}-{self.blue_score}] {self.red_attacker}+{self.red_defender} vs {self.blue_attacker}+{self.blue_defender})"
