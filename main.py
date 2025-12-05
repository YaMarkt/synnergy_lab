import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from config import BOT_TOKEN, ADMIN_IDS
from scheduler import ScriptScheduler
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class MyBot:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.dp = Dispatcher()
        self.config = type('Config', (), {'ADMIN_IDS': ADMIN_IDS})
        self.scheduler = ScriptScheduler(self)
        
        # Регистрация обработчиков
        self.dp.message(Command("start"))(self.start_handler)
        self.dp.message(Command("help"))(self.help_handler)
        self.dp.message(Command("run_script"))(self.run_script_handler)
        self.dp.message(Command("list_scripts"))(self.list_scripts_handler)
        self.dp.message(Command("add_script"))(self.add_script_handler)
        self.dp.message(Command("remove_script"))(self.remove_script_handler)
        # Проверка прав администратора
        self.dp.message.filter(F.from_user.id.in_(ADMIN_IDS))

    # Добавляем этот метод
    async def send_message(self, chat_id: int, text: str):
        try:
            await self.bot.send_message(chat_id=chat_id, text=text)
            return True
        except Exception as e:
            logging.error(f"Failed to send message to {chat_id}: {e}")
            return False

    # ... остальные методы класса ...
    async def start_handler(self, message: Message):
        await message.answer("Привет! Я бот для запуска скриптов по расписанию.")

    async def help_handler(self, message: Message):
        help_text = """
        Доступные команды:
        /start - Начало работы
        /help - Справка
        /list_scripts - Список активных скриптов
        /run_script <имя> - Запустить скрипт сейчас
        /add_script <имя> <cron> - Добавить скрипт в расписание
        Пример cron: '0 12 * * 1' - каждый понедельник в 12:00
        /remove_script <имя> - Удалить скрипт из расписания
        """
        await message.answer(help_text)

    async def run_script_handler(self, message: Message):
        args = message.text.split()[1:]
        if not args:
            await message.answer("Укажите имя скрипта: /run_script <имя>")
            return
        
        script_name = args[0]
        await message.answer(f"Запускаю скрипт {script_name}...")
        await self.scheduler.run_script(script_name)

    async def list_scripts_handler(self, message: Message):
        if not self.scheduler.scripts:
            await message.answer("Нет активных скриптов.")
            return
        
        scripts_list = "\n".join(
            f"{name}: {info['cron']}" 
            for name, info in self.scheduler.scripts.items()
        )
        await message.answer(f"Активные скрипты:\n{scripts_list}")

    async def add_script_handler(self, message: Message):
        args = message.text.split()[1:]
        if len(args) < 2:
            await message.answer("Используйте: /add_script <имя> <cron>")
            return
        
        script_name, cron = args[0], ' '.join(args[1:])
        if self.scheduler.add_script(script_name, cron):
            await message.answer(f"Скрипт {script_name} добавлен с расписанием: {cron}")
        else:
            await message.answer(f"Не удалось добавить скрипт {script_name}. Проверьте наличие файла.")
    async def remove_script_handler(self, message: Message):
        """Обработчик команды /remove_script"""
        args = message.text.split()[1:]
        if not args:
            await message.answer("Укажите имя скрипта: /remove_script <имя>")
            return
        
        script_name = args[0]
        if self.scheduler.remove_script(script_name):
            await message.answer(f"Скрипт {script_name} удалён из расписания")
        else:
            await message.answer(f"Скрипт {script_name} не найден в расписании")

    async def start(self):
        # Загружаем скрипты из папки (можно заменить на загрузку из БД)
        # Пример: self.scheduler.add_script("example_script", "0 12 * * 1")
        self.scheduler.add_script("treners2", "0 14 * * 3")
        self.scheduler.add_script("achivochnaya", "0 14 1 * *")
        self.scheduler.start()
        await self.dp.start_polling(self.bot)

    async def shutdown(self):
        self.scheduler.shutdown()
        await self.bot.session.close()

if __name__ == "__main__":
    bot = MyBot()
    
    import asyncio
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        asyncio.run(bot.shutdown())
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        asyncio.run(bot.shutdown())