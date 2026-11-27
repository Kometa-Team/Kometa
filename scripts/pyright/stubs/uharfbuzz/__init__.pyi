from typing import Any, Sequence

class Face:
    def __init__(self, blob: bytes, index: int = 0) -> None: ...

class Font:
    scale: tuple[int, int]
    def __init__(self, face: Face) -> None: ...

class GlyphInfo:
    codepoint: int
    cluster: int

class GlyphPosition:
    x_advance: int
    y_advance: int
    x_offset: int
    y_offset: int

class Buffer:
    glyph_infos: Sequence[GlyphInfo]
    glyph_positions: Sequence[GlyphPosition]
    def add_str(self, text: str, item_offset: int = 0, item_length: int = -1) -> None: ...
    def guess_segment_properties(self) -> None: ...

def shape(font: Font, buffer: Buffer, features: dict[str, Any] | None = None, shapers: list[str] | None = None) -> None: ...
