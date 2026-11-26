"""Splice recognized temporal entities back into the text as inline markup.

The recogniser returns entities as standoff objects (with character offsets);
this module uses those offsets to reconstruct annotated text in one of two
styles:

* ``'eis1600'`` - the original EIS1600 inline tag (``ÜY4D0748Y`` year,
  ``ÜL2X09L`` month, ``ÜW1D6W`` weekday, ``ÜC2X08C`` century) embedded
  immediately after the matched span.
* ``'xml'`` - the matched span wrapped in an ``<entity>`` element whose
  attributes carry the parsed values (year_hijri, year_ce, month, ...).
"""
from typing import List, Optional
from xml.sax.saxutils import quoteattr

from .entities import TemporalEntity
from .recogniser import recognise

EIS1600 = 'eis1600'
XML = 'xml'
STYLES = (EIS1600, XML)

# Attributes emitted for the XML element, in order. Values that are ``None``
# are omitted.
_XML_ATTRS = ('entity_type', 'year_hijri', 'year_ce', 'month', 'day', 'weekday', 'category', 'trigger')
_XML_ATTR_NAMES = {'entity_type': 'type'}


def _xml_open_tag(entity: TemporalEntity) -> str:
    parts = ['<entity']
    for attr in _XML_ATTRS:
        value = getattr(entity, attr)
        if value is None:
            continue
        name = _XML_ATTR_NAMES.get(attr, attr)
        parts.append(f'{name}={quoteattr(str(value))}')
    return ' '.join(parts) + '>'


def annotate(
    text: str,
    entities: Optional[List[TemporalEntity]] = None,
    style: str = EIS1600,
) -> str:
    """Return *text* with each entity marked up inline in the given *style*.

    If *entities* is not given, :func:`recognise` is run on *text*. Insertions
    are applied from right to left so the offsets of the not-yet-processed
    entities remain valid.

    ``style='eis1600'`` inserts the tag after the entity's ``end`` offset::

        توفي سنة ثمان وأربعين وسبعمائة ÜY4D0748Y

    ``style='xml'`` wraps the span from ``start`` to ``end``::

        <entity type="year" year_hijri="748" year_ce="1347" category="D" trigger="توفي">توفي سنة ...</entity>
    """
    if style not in STYLES:
        raise ValueError(f'unknown markup style {style!r}; expected one of {STYLES}')

    if entities is None:
        entities = recognise(text)

    result = text
    for entity in sorted(entities, key=lambda e: e.start, reverse=True):
        if style == EIS1600:
            result = f'{result[:entity.end]} {entity.to_tag()}{result[entity.end:]}'
        else:
            result = f'{result[:entity.end]}</entity>{result[entity.end:]}'
            result = f'{result[:entity.start]}{_xml_open_tag(entity)}{result[entity.start:]}'
    return result
