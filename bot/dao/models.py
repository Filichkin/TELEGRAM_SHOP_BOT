from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, ForeignKey
from bot.dao.database import Base


class User(Base):
    username: Mapped[str | None]
    first_name: Mapped[str]
    last_name: Mapped[str]
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False
        )

    payments: Mapped[List['Payment']] = relationship(
        'Payment',
        back_populates='user',
        cascade='all, delete-orphan'
    )

    extend_existing = True

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id})'


class Service(Base):
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[int]
    hidden_content: Mapped[str] = mapped_column(Text)
    payments: Mapped[List['Payment']] = relationship(
        'Payment',
        back_populates='service',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return (
            f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
            )


class Payment(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    service_id: Mapped[int] = mapped_column(ForeignKey('services.id'))
    price: Mapped[int]
    payment_id: Mapped[str] = mapped_column(unique=True)
    user: Mapped['User'] = relationship(
        'User',
        back_populates='payments'
        )
    service: Mapped['Service'] = relationship(
        'Service',
        back_populates='payments'
        )

    def __repr__(self):
        return (
            f'<Payment(id={self.id}, user_id={self.user_id}, '
            f'product_id={self.service_id}, date={self.created_at})>'
            )
