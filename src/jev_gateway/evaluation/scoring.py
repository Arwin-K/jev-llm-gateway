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


def score_choice(raw, reference, truncated=False):
    if truncated:
        return {'outcome':'parse_error','parsed_answer':None,'score':None,'error_category':'truncated'}
    text = raw.strip()
    labels = re.findall(r'(?im)^\s*answer\s*:\s*([A-D])\s*\.?\s*$', text)
    if not labels and re.fullmatch(r'[A-D]\.?', text, flags=re.I):
        labels = [text[0]]
    if not labels:
        match = re.fullmatch(r'(?is)the answer is\s+([A-D])\s*\.?', text)
        if match:
            labels = [match.group(1)]
    labels = [label.upper() for label in labels]
    if not labels or len(set(labels)) != 1:
        return {'outcome':'parse_error','parsed_answer':None,'score':None,'error_category':'ambiguous' if labels else 'malformed'}
    if reference not in 'ABCD' or len(reference) != 1:
        return {'outcome':'evaluator_error','parsed_answer':None,'score':None}
    answer = labels[0]
    return {'outcome':'correct' if answer == reference else 'incorrect','parsed_answer':answer,'score':float(answer == reference)}


def score_code(raw, tests, imports=(), timeout=8, executor=execute):
    text = raw.strip()
    fences = re.findall(r'(?s)```(?:python)?\s*\n(.*?)\n```', text, flags=re.I)
    if fences:
        if len(fences) != 1 or re.sub(r'(?s)```(?:python)?\s*\n.*?\n```', '', text, flags=re.I).strip():
            return {'outcome':'parse_error','parsed_answer':None,'score':None,'error_category':'ambiguous_code'}
        code = fences[0].strip()
    elif '```' in text:
        return {'outcome':'parse_error','parsed_answer':None,'score':None,'error_category':'malformed_fence'}
    else:
        code = text
    if not code or len(code) > 100_000:
        return {'outcome':'parse_error','parsed_answer':None,'score':None,'error_category':'empty_or_oversize'}
    result = executor(code, tuple(tests), tuple(imports), timeout=timeout)
    mapping = {'passed':('correct',1.0), 'failed_tests':('incorrect',0.0), 'timeout':('evaluator_error',None), 'crashed':('incorrect',0.0), 'environment_error':('blocked',None)}
    outcome, score = mapping[result['status']]
    return {'outcome':outcome,'parsed_answer':code,'score':score,'error_category':result['status']}
