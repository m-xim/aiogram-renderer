from typing import List, Optional

from pydantic import field_validator, ConfigDict, BaseModel

from aiogram_renderer.widgets.media import FileBytes
from aiogram_renderer.windows.window import Alert


class BotMode(BaseModel):
    """
    Описывает отдельный режим бота.
    """

    name: str
    values: List[str]
    alert_window: Optional[Alert] = None
    has_custom_handler: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("alert_window")
    def validate_alert_window(cls, v):
        # Проверяем, что в alert_window нет виджета FileBytes
        if v:
            for widget in getattr(v, "_widgets", []):
                if isinstance(widget, FileBytes):
                    raise ValueError("В alert_window не может быть файл с байтами")
        return v
