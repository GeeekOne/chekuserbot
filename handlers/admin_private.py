from aiogram import Bot, Router, types
from aiogram.filters import Command

from filters.chat_types import ChatTypeFilter, IsAdmin


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(['private']), IsAdmin())


@admin_router.message(Command("res"))
async def cmd_res(message: types.Message, bot: Bot):
    await message.answer("restart now")


@admin_router.message(Command("root"))
async def cmd_root(message: types.Message, bot: Bot):
    await message.answer("root enabled")