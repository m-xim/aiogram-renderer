from typing import Any
from aiogram.types import InlineKeyboardButton

from aiogram_renderer.core.callback_data import DPanelCD
from aiogram_renderer.types.data import RendererData
from aiogram_renderer.widgets.keyboard.inline.panel import InlinePanel
from aiogram_renderer.widgets.widget import Condition


class DynamicPanel(InlinePanel):
    __slots__ = ("name", "width", "height", "hide_control_buttons", "hide_number_pages")

    # Формат в fsm_data "name": {"page": 1, "text": ["text1", ...], "data": ["data1", ...]}
    def __init__(
        self,
        name: str,
        width: int = 1,
        height: int = 1,
        hide_control_buttons: bool = False,
        hide_number_pages: bool = False,
        show_on: Condition = None,
    ):
        if width < 1:
            raise ValueError("Ширина группы должна быть не меньше 1")
        if width > 8:
            raise ValueError("У Telegram ограничение на длину InlineKeyboard - 8 кнопок")
        if height < 1:
            raise ValueError("Высота группы должна быть не меньше 1")
        if height > 99:
            raise ValueError("У Telegram ограничение на высоту InlineKeyboard - 100 кнопок")

        super().__init__(show_on=show_on)

        self.name = name
        self.width = width
        self.height = height
        self.hide_control_buttons = hide_control_buttons
        self.hide_number_pages = hide_number_pages

    async def _render(self, data: dict[str, Any], rdata: RendererData, **kwargs) -> list[list[Any]]:
        dpanels_data = rdata.dpanels[self.name]

        if len(dpanels_data.text) != len(dpanels_data.data):
            raise ValueError("В группе должно быть одинаковое количество text и data")

        count_buttons = len(dpanels_data.text)

        # Добавляем дополнительную страницу если при делении на число кнопок есть остатки
        last_page = count_buttons // (self.width * self.height)
        last_page = last_page + 1 if (count_buttons % (self.width * self.height)) > 0 else last_page

        # Проверяем не задали ли страницу больше чем есть
        if last_page < dpanels_data.page:
            raise ValueError(f"У группы нет столько страниц, максимальная: {last_page}")

        # Формируем набор кнопок, начиная с заданной страницы и заканчивая срезом по width, height
        start = self.width * self.height * (dpanels_data.page - 1)
        trimmed_b_text = dpanels_data.text[start : start + (self.width * self.height)]
        trimmed_b_data = dpanels_data.data[start : start + (self.width * self.height)]

        buttons = [[]]
        row = 0
        for col, text, callback_data in zip(range(count_buttons), trimmed_b_text, trimmed_b_data):
            button = InlineKeyboardButton(text=text, callback_data=callback_data)

            if col % self.width == 0 and col != 0:
                buttons.append([button])
                row += 1
            else:
                buttons[row].append(button)

        # Формируем кнопки управления
        if (count_buttons > (self.width * self.height)) and (not self.hide_control_buttons):
            if self.hide_number_pages:
                if dpanels_data.page == 1:
                    buttons.append(
                        [
                            InlineKeyboardButton(
                                text=">",
                                callback_data=DPanelCD(page=dpanels_data.page + 1, panel_name=self.name).pack(),
                            ),
                        ]
                    )
                elif dpanels_data.page == last_page:
                    buttons.append(
                        [
                            InlineKeyboardButton(
                                text="<",
                                callback_data=DPanelCD(page=dpanels_data.page - 1, panel_name=self.name).pack(),
                            ),
                        ]
                    )
                else:
                    buttons.append(
                        [
                            InlineKeyboardButton(
                                text="<",
                                callback_data=DPanelCD(page=dpanels_data.page - 1, panel_name=self.name).pack(),
                            ),
                            InlineKeyboardButton(
                                text=">",
                                callback_data=DPanelCD(page=dpanels_data.page + 1, panel_name=self.name).pack(),
                            ),
                        ]
                    )
            else:
                if dpanels_data.page == 1:
                    buttons.append(
                        [
                            InlineKeyboardButton(text="[ 1 ]", callback_data="__disable__"),
                            InlineKeyboardButton(
                                text=">",
                                callback_data=DPanelCD(page=dpanels_data.page + 1, panel_name=self.name).pack(),
                            ),
                            InlineKeyboardButton(
                                text=str(last_page), callback_data=DPanelCD(page=last_page, panel_name=self.name).pack()
                            ),
                        ]
                    )
                elif dpanels_data.page == last_page:
                    buttons.append(
                        [
                            InlineKeyboardButton(text="1", callback_data=DPanelCD(page=1, panel_name=self.name).pack()),
                            InlineKeyboardButton(
                                text="<",
                                callback_data=DPanelCD(page=dpanels_data.page - 1, panel_name=self.name).pack(),
                            ),
                            InlineKeyboardButton(text=f"[ {last_page} ]", callback_data="__disable__"),
                        ]
                    )
                else:
                    buttons.append(
                        [
                            InlineKeyboardButton(text="1", callback_data=DPanelCD(page=1, panel_name=self.name).pack()),
                            InlineKeyboardButton(
                                text="<",
                                callback_data=DPanelCD(page=dpanels_data.page - 1, panel_name=self.name).pack(),
                            ),
                            InlineKeyboardButton(text=f"[ {dpanels_data.page} ]", callback_data="__disable__"),
                            InlineKeyboardButton(
                                text=">",
                                callback_data=DPanelCD(page=dpanels_data.page + 1, panel_name=self.name).pack(),
                            ),
                            InlineKeyboardButton(
                                text=str(last_page), callback_data=DPanelCD(page=last_page, panel_name=self.name).pack()
                            ),
                        ]
                    )

        return buttons
