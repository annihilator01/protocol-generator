import argparse
import datetime as dt

from pydantic import BaseModel
from pydantic import Field
from pydantic import root_validator
from pydantic import validator
from typing import Optional
from typing import Self


class CommandOptions(BaseModel):
    @classmethod
    def parse_args(cls, arg: str) -> Self:
        parser = argparse.ArgumentParser(exit_on_error=False)
        for field in cls.__fields__.keys():
            parser.add_argument(f"--{field}", type=str)

        opts, _ = parser.parse_known_args(arg.split())
        return cls(**{
            key: value
            for key, value in vars(opts).items()
            if value is not None
        })


class GenerateProtocolDataCommandOptions(CommandOptions):
    accounts: Optional[int] = Field(100)
    start: Optional[dt.datetime] = Field(
        default_factory=lambda: dt.datetime.now() - dt.timedelta(days=5),
    )
    end: Optional[dt.datetime] = Field(
        default_factory=lambda: dt.datetime.now(),
    )
    deposit: Optional[float] = Field(2_000_000)

    @validator("start", "end", pre=True)
    def parse_date(cls, value) -> dt.datetime:
        if isinstance(value, str):
            return dt.datetime.fromisoformat(value)
        else:
            return value

    @root_validator
    def validate_dates(cls, values: dict) -> dict:
        if values["end"] < values["start"]:
            raise ValueError("end date cannot be before start date")
        return values


class GetCurrentDepositCommandOptions(CommandOptions):
    protocol: int = Field(...)
