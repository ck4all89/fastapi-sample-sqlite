from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column


from app.db.base import Base



class Mailbox(Base):
    __tablename__ = "mailbox"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    to_email: Mapped[str] = mapped_column(String(255), nullable=False)
    from_email: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    contents: Mapped[str] = mapped_column(Text, nullable=False)
