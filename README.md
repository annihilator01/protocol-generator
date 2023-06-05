# Protocol Data Generator

## Description
CMD tool for generating protocol data such as tokens, accounts,
balance, token price and TVL history

## Launch Instructions
1. Copy .env.example to .env file:
```shell
make init
```

2. Create/activate python (>=python3.11) virtual environment and install dependencies:
```shell
make venv
source ./venv/bin/activate
```

3. Start PostgreSQL in docker container in separate tty (logs included):
```shell
make postgres
```

4. Start CMD tool in separate tty:
```shell
make console
```

5. Command to run pytest:
```shell
make test
```

## Commands
### generate_protocol_data
Generates data for protocol
```
--accounts, number of accounts using protocol (default: 100)
--start, activation date of protocol (default: now - 5 days)
--end, deactivation date of protocol (default: now)
--deposit, last deposit sum in usd (default: 2_000_000)
```

### get_current_deposit
Get current deposit of protocol
```
--protocol, id of requested protocol
```
