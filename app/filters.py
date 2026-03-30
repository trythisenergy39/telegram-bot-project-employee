from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from config import config

# Пользовательский фильтр
class Admin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == config.ADMIN_ID

class AdminC(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.from_user.id == config.ADMIN_ID