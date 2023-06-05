import datetime as dt
import math
import random
import secrets
import string

from decimal import Decimal
from typing import TYPE_CHECKING

from core.db.model import Account
from core.db.model import AccountBalanceHistory
from core.db.model import Protocol
from core.db.model import ProtocolToken
from core.db.model import Token
from core.db.model import TokenPrice
from core.db.repo import BaseRepo
from core.db.repo import ProtocolTokenRepo
from core.db.repo import TVLHistoryRepo

if TYPE_CHECKING:
    from core.shell.model import GenerateProtocolDataCommandOptions


class ProtocolDataGeneratorService:
    def __init__(
        self,
        base_repo: BaseRepo,
        protocol_token_repo: ProtocolTokenRepo,
        tvl_history_repo: TVLHistoryRepo,
    ):
        self.base_repo = base_repo
        self.protocol_token_repo = protocol_token_repo
        self.tvl_history_repo = tvl_history_repo
        self.token_number = random.randint(10, 50)

    async def generate_all(
        self,
        options: "GenerateProtocolDataCommandOptions",
    ) -> int:
        protocol = await self.generate_protocol_with_tokens()
        await self.base_repo.add_all([protocol], with_commit=True)

        accounts = await self.generate_accounts(options.accounts)
        token_prices = await self.generate_balance_history_and_token_price(
            protocol=protocol,
            accounts=accounts,
            start=options.start,
            end=options.end,
            deposit=options.deposit,
        )

        await self.base_repo.add_all(accounts, with_commit=True)
        await self.base_repo.add_all(token_prices, with_commit=True)
        await self.tvl_history_repo.calculate_history_by_protocol_id(
            protocol_id=protocol.id,
        )

        return protocol.id

    async def generate_protocol_with_tokens(self) -> Protocol:
        protocol = Protocol(name=self.generate_name())

        protocol.tokens = []
        for i in range(self.token_number):
            token = Token(
                name=self.generate_name(4, 7),
                symbol=self.generate_name(3, 4).upper(),
                decimals=random.randint(1, 20),
            )
            protocol.tokens.append(token)

        return protocol

    @staticmethod
    async def generate_accounts(accounts_number: int) -> list[Account]:
        accounts = [
            Account(wallet_address=secrets.token_hex(20))
            for _ in range(accounts_number)
        ]
        return accounts

    async def generate_balance_history_and_token_price(
        self,
        protocol: Protocol,
        accounts: list[Account],
        start: dt.datetime,
        end: dt.datetime,
        deposit: float,
    ) -> list[TokenPrice]:
        number_of_tokens_per_account = math.ceil(0.02 * self.token_number)
        final_token_amount = 100
        final_token_price = deposit / (
            len(accounts)
            * number_of_tokens_per_account
            * final_token_amount
        )

        await self._generate_balance_history(
            protocol=protocol,
            accounts=accounts,
            number_of_tokens_per_account=number_of_tokens_per_account,
            final_token_amount=Decimal(final_token_amount),
            start=start,
            end=end,
        )

        tokens_prices = await self._generate_tokens_prices(
            protocol=protocol,
            final_token_price=Decimal(final_token_price),
            start=start,
            end=end,
        )

        return tokens_prices

    async def _generate_balance_history(
        self,
        protocol: Protocol,
        accounts: list[Account],
        number_of_tokens_per_account: int,
        final_token_amount: Decimal,
        start: dt.datetime,
        end: dt.datetime,
    ):
        final_created_at_block = math.ceil(
            (end - start).total_seconds() / 3600
        )
        number_of_changing_accounts = math.ceil(len(accounts) * 0.05)

        protocol_token_list = await (
            self.protocol_token_repo.get_protocol_token_by_protocol_id(
                protocol_id=protocol.id
            )
        )

        await self._generate_account_token_balance(
            protocol_token_list=protocol_token_list,
            accounts=accounts,
            number_of_tokens_per_account=number_of_tokens_per_account,
            token_amount=final_token_amount,
            created_at=end,
            created_at_block=final_created_at_block,
        )

        for current_block in reversed(range(final_created_at_block)):
            token_amount = (
                final_token_amount
                * (100 - random.randint(-15, 15))
                / 100
            )
            created_at = end - dt.timedelta(
                seconds=(final_created_at_block - current_block) * 3600
            )

            await self._generate_account_token_balance(
                protocol_token_list=protocol_token_list,
                accounts=random.sample(
                    accounts,
                    number_of_changing_accounts,
                ),
                number_of_tokens_per_account=number_of_tokens_per_account,
                token_amount=token_amount,
                created_at=created_at,
                created_at_block=current_block,
            )

    @staticmethod
    async def _generate_account_token_balance(
        protocol_token_list: list[ProtocolToken],
        accounts: list[Account],
        number_of_tokens_per_account: int,
        token_amount: Decimal,
        created_at: dt.datetime,
        created_at_block: int,
    ):
        for account in accounts:
            account.balance_history = account.balance_history or []

            for protocol_token in random.sample(
                protocol_token_list,
                number_of_tokens_per_account,
            ):
                protocol_token: ProtocolToken
                account.balance_history.append(
                    AccountBalanceHistory(
                        protocol_token_id=protocol_token.id,
                        amount=token_amount,
                        created_at=created_at,
                        created_at_block=created_at_block,
                    )
                )

    @staticmethod
    async def _generate_tokens_prices(
        protocol: Protocol,
        final_token_price: Decimal,
        start: dt.datetime,
        end: dt.datetime,
    ) -> list[TokenPrice]:
        tokens_prices: list[TokenPrice] = []
        tick_in_minutes = 10
        segments_number = math.ceil(
            (end - start).total_seconds()
            / (60 * tick_in_minutes)
        )

        for token in protocol.tokens:
            for delta in range(segments_number):
                created_at = end - dt.timedelta(
                    minutes=delta * tick_in_minutes
                )
                usd_price = (
                    final_token_price
                    * (100 - random.randint(-15, 15))
                    / 100
                )
                tokens_prices.append(
                    TokenPrice(
                        token_id=token.id,
                        usd_price=usd_price if delta else final_token_price,
                        created_at=created_at,
                    )
                )
        return tokens_prices

    @staticmethod
    def generate_name(from_k: int = 5, to_k: int = 5) -> str:
        name_len = random.choice(range(from_k, to_k + 1))
        name_letters = random.choices(string.ascii_letters, k=name_len)
        return "".join(name_letters)
