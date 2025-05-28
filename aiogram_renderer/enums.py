from enum import Enum


class KeyboardType(str, Enum):
    REPLY = "reply"
    INLINE = "inline"


class RenderMode(str, Enum):
    EDIT = "edit"
    DELETE_AND_SEND = "delete_and_send"
    ANSWER = "answer"
    REPLY = "reply"