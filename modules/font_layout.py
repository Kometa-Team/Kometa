import unicodedata
from functools import lru_cache
from io import BytesIO
from math import ceil

import uharfbuzz
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

from modules.util import Failed


class FontMetrics:
    """Lays out text with a font's own kerning, ligatures and contextual forms without needing Pillow's RAQM layout engine.

    Pillow draws every glyph using BASIC layout; each glyph is exposed to Pillow through a private-use cmap entry in an in-memory copy of the font.
    """

    def __init__(self, path, shaping=False):
        self.shaping = shaping
        with open(path, "rb") as handle:
            self.original_data = handle.read()
        self._hb_font = None
        with TTFont(BytesIO(self.original_data)) as font:
            self.glyph_order = font.getGlyphOrder()
            self.cmap: dict[int, str] = font.getBestCmap() or {}
            self.advances = dict(font["hmtx"].metrics)
            head, post = font["head"], font["post"]
            self.units = getattr(head, "unitsPerEm")
            self.underline = getattr(post, "underlinePosition") - getattr(post, "underlineThickness") / 2
            self.left = {name: getattr(font["glyf"][name], "xMin", 0) for name in self.glyph_order} if "glyf" in font else {}
            self.pairs, self.tables, self.substitutions = {}, [], []
            if "GPOS" in font:
                table = font["GPOS"].table
                indices = {i for r in table.FeatureList.FeatureRecord if r.FeatureTag == "kern" for i in r.Feature.LookupListIndex}
                for index in sorted(indices):
                    lookup = table.LookupList.Lookup[index]
                    for subtable in lookup.SubTable:
                        if lookup.LookupType == 2:
                            self.tables.append(subtable)
                        elif lookup.LookupType == 9 and subtable.ExtensionLookupType == 2:
                            self.tables.append(subtable.ExtSubTable)
            if not self.tables and "kern" in font:
                for table in font["kern"].kernTables:
                    if table.coverage & 1:
                        self.pairs.update(table.kernTable)
            self.gsub = font["GSUB"].table if "GSUB" in font else None
            if self.gsub:
                scripts = {r.ScriptTag: r.Script for r in self.gsub.ScriptList.ScriptRecord}
                script = scripts.get("latn", scripts.get("DFLT"))
                indices = script.DefaultLangSys.FeatureIndex if script and script.DefaultLangSys else []
                for tag in ("ccmp", "locl", "rlig", "liga", "clig", "calt"):
                    for index in indices:
                        record = self.gsub.FeatureList.FeatureRecord[index]
                        if record.FeatureTag == tag:
                            self.substitutions.extend(record.Feature.LookupListIndex)
            self.characters = {glyph: chr(0xF0000 + index) for index, glyph in enumerate(self.glyph_order)}
            bridge = CmapSubtable.newSubtable(12)
            bridge.platformID, bridge.platEncID, bridge.language = 3, 10, 0
            bridge.cmap = {**self.cmap, **{ord(character): glyph for glyph, character in self.characters.items()}}
            font["cmap"].tables = [t for t in font["cmap"].tables if (t.platformID, t.platEncID, t.language) != (3, 10, 0)]
            font["cmap"].tables.append(bridge)
            buffer = BytesIO()
            font.save(buffer)
            self.font_data = buffer.getvalue()

    def _substitute(self, glyphs, index, lookup_index, depth=0):
        if self.gsub is None or index >= len(glyphs) or depth > 8:
            return
        lookup = self.gsub.LookupList.Lookup[lookup_index]
        for table in lookup.SubTable:
            kind = lookup.LookupType
            if kind == 7:
                kind, table = table.ExtensionLookupType, table.ExtSubTable
            if kind == 1:
                replacement = table.mapping.get(glyphs[index])
                if replacement:
                    glyphs[index] = replacement
                    return
            elif kind == 4:
                for ligature in table.ligatures.get(glyphs[index], []):
                    count = len(ligature.Component)
                    if glyphs[index + 1 : index + 1 + count] == ligature.Component:
                        glyphs[index : index + 1 + count] = [ligature.LigGlyph]
                        return
            elif kind == 6:
                if table.Format == 3:
                    rules = [(table.BacktrackCoverage, table.InputCoverage, table.LookAheadCoverage, table.SubstLookupRecord)]
                    covered = True
                elif table.Format == 1:
                    covered = glyphs[index] in table.Coverage.glyphs
                    group = table.ChainSubRuleSet[table.Coverage.glyphs.index(glyphs[index])] if covered else None
                    rules = [([{g} for g in r.Backtrack], [{glyphs[index]}, *[{g} for g in r.Input]], [{g} for g in r.LookAhead], r.SubstLookupRecord) for r in group.ChainSubRule] if group else []
                else:
                    raise Failed("Font Error: Unsupported contextual font layout")

                def matches(coverage, glyph):
                    return glyph in (coverage.glyphs if hasattr(coverage, "glyphs") else coverage)

                for back, inputs, ahead, records in rules:
                    if (
                        covered
                        and index >= len(back)
                        and index + len(inputs) + len(ahead) <= len(glyphs)
                        and all(matches(c, glyphs[index - 1 - j]) for j, c in enumerate(back))
                        and all(matches(c, glyphs[index + j]) for j, c in enumerate(inputs))
                        and all(matches(c, glyphs[index + len(inputs) + j]) for j, c in enumerate(ahead))
                    ):
                        for record in records:
                            self._substitute(glyphs, index + record.SequenceIndex, record.LookupListIndex, depth + 1)
                        return

    def requires_shaping(self, text):
        text = unicodedata.normalize("NFC", text)
        return self.shaping or any(ord(c) not in self.cmap or unicodedata.combining(c) or unicodedata.bidirectional(c) in {"R", "AL", "AN"} or 0x900 <= ord(c) <= 0x109F for c in text)

    def glyphs(self, text):
        if self.requires_shaping(text):
            return [self.glyph_order[g] for g, *_ in self.shaped(text)]
        text = unicodedata.normalize("NFC", text)
        missing = [c for c in text if ord(c) not in self.cmap]
        if missing:
            raise Failed(f"Font Error: Font has no glyph for {missing[0]!r}")
        result = [self.cmap[ord(c)] for c in text]
        for lookup in self.substitutions:
            index = 0
            while index < len(result):
                self._substitute(result, index, lookup)
                index += 1
        return result

    @lru_cache(maxsize=1024)
    def shaped(self, text):
        if self._hb_font is None:
            self._hb_font = uharfbuzz.Font(uharfbuzz.Face(self.original_data))
            self._hb_font.scale = (self.units, self.units)
        buffer = uharfbuzz.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        uharfbuzz.shape(self._hb_font, buffer)
        result = tuple((info.codepoint, p.x_advance, p.x_offset, p.y_offset) for info, p in zip(buffer.glyph_infos, buffer.glyph_positions))
        if any(g == 0 for g, *_ in result):
            raise Failed("Font Error: Font has no glyph for part of the text")
        return result

    def layout(self, text, size):
        """Returns ``([(character, x, y), ...], advance)`` where each character is the private-use alias of one glyph."""
        if not self.requires_shaping(text):
            positions, advance = self.positions(text, size)
            return [(c, x, 0) for c, x in positions], advance
        positions, advance = [], 0
        scale = size / self.units
        for glyph, width, x, y in self.shaped(text):
            positions.append((self.characters[self.glyph_order[glyph]], advance + x * scale, -y * scale))
            advance += width * scale
        return positions, advance

    def kern(self, left, right):
        value = self.pairs.get((left, right), 0)
        for table in self.tables:
            if left not in table.Coverage.glyphs:
                continue
            if table.Format == 1:
                pairs = table.PairSet[table.Coverage.glyphs.index(left)].PairValueRecord
                record = next((p for p in pairs if p.SecondGlyph == right), None)
            else:
                first, second = table.ClassDef1.classDefs.get(left, 0), table.ClassDef2.classDefs.get(right, 0)
                record = table.Class1Record[first].Class2Record[second]
            value += getattr(getattr(record, "Value1", None), "XAdvance", 0) or 0
        return value

    def positions(self, text, size):
        if self.requires_shaping(text):
            positions, advance = self.layout(text, size)
            return [(c, x) for c, x, _ in positions], advance
        positions, advance, previous = [], 0, None
        scale = size / self.units
        for glyph in self.glyphs(text):
            if previous is not None:
                advance += self.kern(previous, glyph) * scale
            positions.append((self.characters[glyph], advance))
            advance += self.advances[glyph][0] * scale
            previous = glyph
        return positions, advance

    def width(self, text, size):
        return max((self.positions(line, size)[1] for line in text.splitlines()), default=0)

    def fitted_extent(self, text, size, height):
        widths = []
        for line in text.splitlines():
            glyphs = self.glyphs(line)
            width = self.positions(line, size)[1]
            bearing = min((self.left.get(g, 0) for g in glyphs), default=0) * size / self.units
            widths.append(width + (2 * ceil(-bearing + 0.5) if bearing < 0 else 0))
        return max(widths, default=0) + 1, height * len(text.splitlines()) - self.underline * size / self.units + 1
