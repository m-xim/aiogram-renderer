from aiogram.enums import ContentType
from textcompose import Template
from textcompose.elements import Text, Format

from aiogram_renderer.widgets.media.group import MediaGroup
from aiogram_renderer.widgets.media.media import Media
from states import MenuStates
from aiogram_renderer.widgets.keyboard.inline import ComeTo, Mode, DynamicPanel
from aiogram_renderer.widgets.keyboard.reply import ReplyMode
from aiogram_renderer.windows.window import Window, Alert

main_window = Window(
    Template(Text("Главное меню")),
    Mode(name="h200"),
    DynamicPanel(name="test_dg", width=2, height=2, hide_number_pages=True),
    ComeTo(text="Перейти в меню 2", state=MenuStates.main2),
    state=MenuStates.main1,
)

main_window2 = Window(
    Template(Text("Главное меню 2")),
    MediaGroup(
        Media(path=Format("img.png"), media_type=ContentType.PHOTO),
        Media(path=Format("img.png"), caption="222", media_type=ContentType.PHOTO),
    ),
    # Media(path=Text("img.png"), media_type=ContentType.PHOTO),
    ComeTo(text="Перейти в меню 1", state=MenuStates.main1),
    state=MenuStates.main2,
)

alert_mode = Alert(
    Template(Text("Nice")),
    # FileBytes(file_name="{filename}", bytes_name="test_fb", when='test_when'),
    ReplyMode(name="h200"),
)
