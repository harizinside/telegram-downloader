from aiogram.fsm.state import State, StatesGroup


class DownloadFlow(StatesGroup):
    downloading = State()
