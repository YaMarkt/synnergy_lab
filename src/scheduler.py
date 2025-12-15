from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Callable, Dict
import importlib.util
from pathlib import Path
import asyncio
import logging

class ScriptScheduler:
    def __init__(self, bot, scripts_dir: str = "scripts"):
        self.bot = bot
        self.scripts_dir = Path(scripts_dir)
        self.scheduler = AsyncIOScheduler()
        self.scripts: Dict[str, Dict] = {}
        
        if not self.scripts_dir.exists():
            self.scripts_dir.mkdir()
            logging.warning(f"Created scripts directory at {self.scripts_dir}")

    async def run_script(self, script_name: str): #Попытка запуска скрипта если настало время
        """Запускает скрипт и обрабатывает результат"""
        logging.info(f"Попытка запуска скрипта: {script_name}")
        
        script_info = self.scripts.get(script_name)
        if not script_info:
            error_msg = f"Скрипт {script_name} не найден в расписании"
            logging.error(error_msg)
            return False

        script_path = self.scripts_dir / f"{script_name}.py"
        logging.info(f"Путь к скрипту: {script_path}")
        
        if not script_path.exists():
            error_msg = f"Файл скрипта не существует: {script_path}"
            logging.error(error_msg)
            return False
        
        try:
            # Динамически импортируем модуль
            spec = importlib.util.spec_from_file_location(script_name, script_path)
            if spec is None:
                error_msg = f"Не удалось создать spec для {script_name}"
                logging.error(error_msg)
                return False
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            logging.info(f"Модуль {script_name} успешно загружен")
            
            # Проверяем наличие функции main
            if not hasattr(module, 'main'):
                error_msg = f"В скрипте {script_name} не найдена функция main()"
                logging.error(error_msg)
                return False
                
            # Запускаем main
            if asyncio.iscoroutinefunction(module.main):
                result = await module.main()
            else:
                result = module.main()
                
            success_msg = f"✅ Скрипт {script_name} выполнен успешно.\nРезультат: {result}"
            logging.info(success_msg)
            
            # Отправляем уведомление администраторам
            for admin_id in self.bot.config.ADMIN_IDS:
                try:
                    await self.bot.bot.send_message(chat_id=admin_id, text=success_msg)
                except Exception as e:
                    logging.error(f"Ошибка отправки сообщения admin {admin_id}: {e}")
            
            return True
            
        except Exception as e:
            error_msg = f"❌ Ошибка при выполнении скрипта {script_name}:\n{str(e)}"
            logging.exception(error_msg)
            
            # Отправляем уведомление об ошибке
            for admin_id in self.bot.config.ADMIN_IDS:
                try:
                    await self.bot.bot.send_message(chat_id=admin_id, text=error_msg)
                except Exception as e:
                    logging.error(f"Ошибка отправки сообщения об ошибке admin {admin_id}: {e}")
            
            return False

    def add_script(self, script_name: str, cron_expression: str): #функция для добавления скрипта в расписание через бота
        """Добавляет скрипт в расписание"""
        script_path = self.scripts_dir / f"{script_name}.py"
        if not script_path.exists():
            logging.error(f"Script file not found: {script_path}")
            return False

        self.scripts[script_name] = {
            'cron': cron_expression,
            'path': script_path
        }
        
        # Добавляем задачу в планировщик
        self.scheduler.add_job(
            self.run_script,
            CronTrigger.from_crontab(cron_expression),
            args=[script_name],
            id=script_name
        )
        return True
    def remove_script(self, script_name: str):
        """Удаляет скрипт из расписания"""
        if script_name not in self.scripts:
            return False
            
        # Удаляем задачу из планировщика
        self.scheduler.remove_job(script_name)
        
        # Удаляем из словаря скриптов
        del self.scripts[script_name]
        
        return True

    def start(self):
        """Запускает планировщик"""
        self.scheduler.start()
        logging.info("Scheduler started")

    def shutdown(self):
        """Останавливает планировщик"""
        self.scheduler.shutdown()
        logging.info("Scheduler stopped")