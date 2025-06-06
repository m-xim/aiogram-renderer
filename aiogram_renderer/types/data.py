from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List


class DynamicPanelsData(BaseModel):
    page: int
    text: List[str] = Field(default_factory=list)
    data: List[str] = Field(default_factory=list)


class RendererData(BaseModel):
    modes: Optional[Dict[str, list[str]]] = Field(default_factory=dict)
    windows: Optional[Dict[str, Dict[str, Any]]] = Field(default_factory=dict[str, Any])
    dpanels: Optional[Dict[str, DynamicPanelsData]] = Field(default_factory=dict[str, DynamicPanelsData])

    class Config:
        pass
        # extra = "allow"  # чтобы не ругался на лишние ключи
