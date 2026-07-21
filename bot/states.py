from aiogram.fsm.state import State, StatesGroup


class DownloadFlow(StatesGroup):
    downloading = State()
    awaiting_tldv_token = State()
    awaiting_tldv_url = State()
