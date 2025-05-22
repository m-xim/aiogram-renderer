class Widget:
    __slots__ = ("when",)

    # Фильтры when дополнительно сохраняются в ОП, для доступа из alerts
    def __init__(self, when: str = None):
        self.when = when
