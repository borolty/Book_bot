from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str            # Токен для доступа к телеграм-боту
    #admin_ids: list[int]  # Список id администраторов бота

@dataclass
class LogSettings:
    level: str
    format: str

@dataclass
class Config:
    bot: TgBot
    log: LogSettings


def load_config(path: str | None = None) -> Config:
    env: Env = Env()
    env.read_env(path)
    return Config(
        bot=TgBot(token=env('BOT_TOKEN')),
        #admin_ids=list(map(int, env.list('ADMIN_IDS')))),
        log=LogSettings(level=env("LOG_LEVEL"), format=env("LOG_FORMAT")))