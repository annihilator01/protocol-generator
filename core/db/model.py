import datetime as dt
import inflection
import sqlalchemy as sa
import sqlmodel as sm

from decimal import Decimal
from pydantic import condecimal
from sqlalchemy.orm import declared_attr
from typing import Optional


uint256: type[Decimal] = condecimal(
    max_digits=78,
    decimal_places=0,
    ge=Decimal(0), lt=Decimal(2 ** 256),
)


class BaseSQLModel(sm.SQLModel):
    @declared_attr
    def __tablename__(cls) -> str:
        return inflection.underscore(cls.__name__)


class ProtocolToken(BaseSQLModel, table=True):
    id: Optional[int] = sm.Field(default=None, primary_key=True)
    protocol_id: Optional[int] = sm.Field(
        nullable=False,
        foreign_key="protocol.id",
        index=True,
    )
    token_id: Optional[int] = sm.Field(nullable=False, foreign_key="token.id")

    balance_history: list["AccountBalanceHistory"] = sm.Relationship(
        back_populates="protocol_token",
    )
    tvl_history: list["TVLHistory"] = sm.Relationship(
        back_populates="protocol_token",
    )


class Protocol(BaseSQLModel, table=True):
    id: Optional[int] = sm.Field(default=None, primary_key=True)
    name: str = sm.Field(nullable=False, unique=True)

    tokens: Optional[list["Token"]] = sm.Relationship(
        back_populates="protocols",
        link_model=ProtocolToken,
    )


class Token(BaseSQLModel, table=True):
    id: Optional[int] = sm.Field(default=None, primary_key=True)
    name: str = sm.Field(nullable=False, unique=True)
    symbol: str = sm.Field(nullable=False, unique=True)
    decimals: int = sm.Field(nullable=False)

    protocols: Optional[list["Protocol"]] = sm.Relationship(
        back_populates="tokens",
        link_model=ProtocolToken,
    )
    prices: Optional[list["TokenPrice"]] = sm.Relationship(
        back_populates="token",
    )


class Account(BaseSQLModel, table=True):
    id: Optional[int] = sm.Field(
        default=None,
        sa_column=sa.Column(
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
        ),
    )
    wallet_address: str = sm.Field(nullable=False, unique=True)

    balance_history: Optional[list["AccountBalanceHistory"]] = sm.Relationship(
        back_populates="account",
    )


class AccountBalanceHistory(BaseSQLModel, table=True):
    id: Optional[int] = sm.Field(
        default=None,
        sa_column=sa.Column(
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
        ),
    )
    protocol_token_id: Optional[int] = sm.Field(
        nullable=False,
        foreign_key="protocol_token.id",
        index=True,
    )
    account_id: Optional[int] = sm.Field(
        sa_column=sa.Column(
            sa.BigInteger(),
            sa.ForeignKey("account.id"),
            nullable=False,
            index=True,
        ),
    )
    amount: uint256 = sm.Field(nullable=False)
    created_at: dt.datetime = sm.Field(
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            nullable=False,
            index=True,
        ),
    )
    created_at_block: int = sm.Field(
        sa_column=sa.Column(
            sa.BigInteger(),
            nullable=False,
            index=True,
        ),
    )

    protocol_token: Optional[ProtocolToken] = sm.Relationship(
        back_populates="balance_history",
    )
    account: Optional[Account] = sm.Relationship(
        back_populates="balance_history",
    )


class TokenPrice(BaseSQLModel, table=True):
    id: Optional[int] = sm.Field(
        default=None,
        sa_column=sa.Column(
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
        ),
    )
    token_id: Optional[int] = sm.Field(
        nullable=False,
        foreign_key="token.id",
        index=True,
    )
    usd_price: Decimal = sm.Field(nullable=False)
    created_at: dt.datetime = sm.Field(
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            nullable=False,
            index=True,
        ),
    )

    token: Optional[Token] = sm.Relationship(back_populates="prices")


class TVLHistory(BaseSQLModel, table=True):
    id: Optional[int] = sm.Field(
        default=None,
        sa_column=sa.Column(
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
        ),
    )
    protocol_token_id: Optional[int] = sm.Field(
        nullable=False,
        foreign_key="protocol_token.id",
        index=True,
    )
    amount: Decimal = sm.Field(nullable=False)
    amount_usd: Decimal = sm.Field(nullable=False)
    created_at: dt.datetime = sm.Field(
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            nullable=False,
            index=True,
        ),
    )
    created_at_block: int = sm.Field(
        sa_column=sa.Column(
            sa.BigInteger(),
            nullable=False,
            index=True,
        ),
    )

    protocol_token: Optional[ProtocolToken] = sm.Relationship(
        back_populates="tvl_history",
    )
