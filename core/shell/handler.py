import asyncio
import cmd
import functools

from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable

from core.db import init_db
from core.db import inject_session
from core.db.repo import BaseRepo
from core.db.repo import ProtocolTokenRepo
from core.db.repo import TVLHistoryRepo
from core.service import ProtocolDataGeneratorService
from core.service import ProtocolPriceService

from .model import GenerateProtocolDataCommandOptions
from .model import GetCurrentDepositCommandOptions


def print_exception(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as exc:
            print(f"\033[91m{exc}\033[0m")
    return wrapper


class _ProtocolGeneratorShellHandler(cmd.Cmd):
    intro = (
        "Welcome to the Protocol Generator shell. "
        "Type help or ? to list commands.\n"
    )
    prompt = "₿ > "

    # ----- SHELL RUNNERS -----
    def preloop(self):
        asyncio.run(init_db())

    # ----- SHELL COMMAND ENTRYPOINTS -----
    @print_exception
    def do_generate_protocol_data(self, arg: str):
        """
        Generates data for protocol
        --accounts, number of accounts using protocol (default: 100)
        --start, activation date of protocol (default: now - 5 days)
        --end, deactivation date of protocol (default: now)
        --deposit, last deposit sum in usd (default: 2_000_000)
        """
        opts = GenerateProtocolDataCommandOptions.parse_args(arg)
        protocol_id = asyncio.run(self._generate_protocol_data(opts))
        print(f"protocol_id={protocol_id}")

    @print_exception
    def do_get_current_deposit(self, arg: str):
        """
        Get current deposit of protocol
        --protocol, id of requested protocol
        """
        opts = GetCurrentDepositCommandOptions.parse_args(arg)
        deposit = asyncio.run(self._get_current_deposit(opts))
        print(f"protocol={opts.protocol}, deposit={deposit}")

    # ----- SHELL COMMAND HANDLERS -----
    @inject_session
    async def _generate_protocol_data(
        self,
        opts: GenerateProtocolDataCommandOptions,
        *,
        session: AsyncSession,
    ) -> int:
        base_repo = BaseRepo(session)
        protocol_token_repo = ProtocolTokenRepo(session)
        tvl_history_repo = TVLHistoryRepo(session)
        protocol_generator_service = ProtocolDataGeneratorService(
            base_repo,
            protocol_token_repo,
            tvl_history_repo,
        )
        return await protocol_generator_service.generate_all(opts)

    @inject_session
    async def _get_current_deposit(
        self,
        opts: GetCurrentDepositCommandOptions,
        *,
        session: AsyncSession,
    ) -> Decimal:
        tvl_history_repo = TVLHistoryRepo(session)
        protocol_generator_service = ProtocolPriceService(tvl_history_repo)
        return await protocol_generator_service.get_protocol_price(opts)


protocol_generator_shell_handler = _ProtocolGeneratorShellHandler()
