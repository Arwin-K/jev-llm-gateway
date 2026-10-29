"""Conservative task scorers: no guessed answers."""
import re
from decimal import Decimal, InvalidOperation
from fractions import Fraction

from .sandbox import execute

_NUMBER = r'[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:\s*/\s*[+-]?\d+)?'


def _number(text):
    token = text.strip().replace(',', '').replace(' ', '')
    if not re.fullmatch(_NUMBER.replace('(?:,\\d{3})+', ''), token):
        return None
    try:
        value = Fraction(token) if '/' in token else Fraction(Decimal(token))
        return value if value.denominator != 0 else None
    except (ValueError, ZeroDivisionError, InvalidOperation):
        return None


def score_math(raw, reference):
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    candidates = [re.sub(r'^answer\s*:\s*', '', line, flags=re.I).rstrip('.') for line in lines if re.match(r'^answer\s*:', line, flags=re.I)]
    if not candidates and len(lines) == 1:
        candidates = [lines[0].rstrip('.')]
    values = [_number(x) for x in candidates]
    ref = _number(str(reference))
    if ref is None:
        return {'outcome':'evaluator_error','parsed_answer':None,'score':None}
    if not values or any(v is None for v in values):
        return {'outcome':'parse_error','parsed_answer':None,'score':None}
    if len(set(values)) != 1:
        return {'outcome':'parse_error','parsed_answer':None,'score':None}
    value = values[0]
    return {'outcome':'correct' if value == ref else 'incorrect','parsed_answer':str(value),'score':float(value == ref)}
