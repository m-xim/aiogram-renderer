from typing import Any
from .widget import Widget


class Text(Widget):
    __slots__ = ("content", "end", "end_count")

    def __init__(self, content: str, end: str = "\n", end_count: int = 0, when: str = None):
        # Добавляем окончание, в зависимости от end_count
        self.content = content
        self.end = end
        self.end_count = end_count
        super().__init__(when=when)

    async def assemble(self, data: dict[str, Any]) -> str:
        text = self.content

        if self.when in data.keys():
            # Если when = False, не собираем текст и возвращаем пустую строку
            if not data[self.when]:
                return ""

        # Форматируем по data, если там заданы ключи {key}
        for key, value in data.items():
            if "{" + key + "}" in text:
                text = text.replace("{" + key + "}", value)

        return text + "".join([self.end for _ in range(self.end_count)])


class Multi(Widget):
    __slots__ = ('texts', 'sep', 'sep_count', 'end', 'end_count')

    def __init__(self, *texts: Text | str, sep: str = "\n", sep_count: int = 1, end: str = "\n",
                 end_count: int = 0, when: str = None):
        self.texts = list(texts)
        self.sep = sep
        self.sep_count = sep_count
        self.end = end
        self.end_count = end_count
        super().__init__(when=when)

    async def assemble(self, data: dict[str, Any]):
        # Формируем разделители, учитывая их количество и после содержимое
        separators = "".join([self.sep for _ in range(self.sep_count)])

        texts_list = []
        for text in self.texts:
            # Если это виджет
            if isinstance(text, Text):
                # Если when в ключах data, то делаем проверку
                if text.when in data.keys():
                    # Если when = False, не собираем text
                    if not data[text.when]:
                        continue
                asm_text = await text.assemble(data=data)
                texts_list.append(asm_text + separators)
            # Если это строка
            else:
                # Форматируем по data, если там заданы ключи {key}
                for key, value in data.items():
                    if "{" + key + "}" in text:
                        text = text.replace("{" + key + "}", value)

                texts_list.append(text + separators)

        # Если все тексты скрыты выдаем пустую строку
        if len(texts_list) == 0:
            return ""
        # В другом случае разделяем контент сепараторами и добавляем end
        else:
            content = "".join(texts_list)[:-self.sep_count] + "".join([self.end for _ in range(self.end_count)])

        return content


class Bold(Text):
    __slots__ = ()

    def __init__(self, content: str, end: str = "\n", end_count: int = 0, when: str = None):
        super().__init__(content=f"<b>{content}</b>", end=end, end_count=end_count, when=when)


class Italic(Text):
    __slots__ = ()

    def __init__(self, content: str, end: str = "\n", end_count: int = 0, when: str = None):
        super().__init__(content=f"<i>{content}</i>", end=end, end_count=end_count, when=when)


class Code(Text):
    __slots__ = ()

    def __init__(self, content: str, end: str = "\n", end_count: int = 0, when: str = None):
        super().__init__(content=f"<code>{content}</code>", end=end, end_count=end_count, when=when)


class Underline(Text):
    __slots__ = ()

    def __init__(self, content: str, end: str = "\n", end_count: int = 0, when: str = None):
        super().__init__(content=f"<u>{content}</u>", end=end, end_count=end_count, when=when)


class Blockquote(Text):
    __slots__ = ()

    def __init__(self, content: str, end: str = "\n", end_count: int = 0, when: str = None):
        super().__init__(content=f"<blockquote>{content}</blockquote>", end=end, end_count=end_count, when=when)
