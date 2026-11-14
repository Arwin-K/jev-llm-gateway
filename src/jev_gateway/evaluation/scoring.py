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


def score_math_strict(raw, reference):
    """v1 scorer: only a whole line `Answer: <bare number>`; kept as the format-compliance measure."""
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


def score_choice_strict(raw, reference, truncated=False):
    """v1 scorer; kept as the format-compliance measure."""
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


_LEAD = re.compile(r'^[\s*_`]*(?:\\\(|\$)?[\s*_`]*\\?\$?\s*')
_MARKER = re.compile(r'(?i)\banswer\s*:\s*(.*)$')
_BOXED = re.compile(r'\\boxed\{((?:[^{}]|\{[^{}]*\})*)\}')


def _after_marker(tail):
    """Number right after `Answer:`; trailing units or punctuation are allowed, further digits are not."""
    if '\\boxed' in tail:
        return 'boxed'
    tail = _LEAD.sub('', tail)
    match = re.match(_NUMBER, tail)
    if not match:
        return None
    rest = tail[match.end():]
    if re.search(r'\d', rest):
        return None
    return _number(match.group(0))


def _boxed(content):
    content = re.sub(r'\\text\{[^{}]*\}', '', content)
    content = re.sub(r'\\[,!;]|\\?\$|\\%|%', '', content)
    return _number(content)


def score_math(raw, reference):
    """Final-answer scorer: every `Answer:` marker and `\\boxed{}` must give one agreeing number.

    Accepts units, currency and thousands separators after the marker. Rejects responses with
    no marker (unless the whole response is one number), unparseable markers, or conflicting values.
    """
    ref = _number(str(reference))
    if ref is None:
        return {'outcome':'evaluator_error','parsed_answer':None,'score':None}
    values = []
    for line in raw.splitlines():
        for match in _MARKER.finditer(line):
            value = _after_marker(match.group(1))
            if value != 'boxed':
                values.append(value)
    values += [_boxed(content) for content in _BOXED.findall(raw)]
    if not values:
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        if len(lines) == 1:
            values = [_number(lines[0].rstrip('.'))]
    if not values or any(v is None for v in values) or len(set(values)) != 1:
        return {'outcome':'parse_error','parsed_answer':None,'score':None,'error_category':'conflicting' if len({v for v in values if v is not None}) > 1 else 'malformed'}
    value = values[0]
    return {'outcome':'correct' if value == ref else 'incorrect','parsed_answer':str(value),'score':float(value == ref)}


_CHOICE = re.compile(r'\b(?i:answer)\s*:\s*[*_`(\[]*\s*([A-D])(?![A-Za-z0-9])(.*)$')


def score_choice(raw, reference, truncated=False):
    """Choice scorer: every `Answer:` marker must name the same single option letter."""
    if truncated:
        return {'outcome':'parse_error','parsed_answer':None,'score':None,'error_category':'truncated'}
    text = raw.strip()
    labels = []
    for line in text.splitlines():
        match = _CHOICE.search(line)
        if match:
            if re.match(r'^\s*[)\].*_`]*\s*(?:,|/|\bor\b|\band\b)\s*\(?[A-D]\b', match.group(2)):
                return {'outcome':'parse_error','parsed_answer':None,'score':None,'error_category':'ambiguous'}
            labels.append(match.group(1).upper())
    if not labels:
        return score_choice_strict(raw, reference, truncated)
    if len(set(labels)) != 1:
        return {'outcome':'parse_error','parsed_answer':None,'score':None,'error_category':'ambiguous'}
    if reference not in 'ABCD' or len(reference) != 1:
        return {'outcome':'evaluator_error','parsed_answer':None,'score':None}
    answer = labels[0]
    return {'outcome':'correct' if answer == reference else 'incorrect','parsed_answer':answer,'score':float(answer == reference)}


def format_compliant(task, raw, reference, truncated=False):
    """Whether the response meets the strict v1 format (bare final line, or code only); None when not applicable."""
    if raw is None or task not in ('math', 'choice', 'code'):
        return None
    if task == 'code':
        text = raw.strip()
        fences = re.findall(r'(?s)```(?:python)?\s*\n(.*?)\n```', text, flags=re.I)
        if not fences:
            return '```' not in text and bool(text)
        return len(fences) == 1 and not re.sub(r'(?s)```(?:python)?\s*\n.*?\n```', '', text, flags=re.I).strip()
    strict = score_math_strict(raw, reference) if task == 'math' else score_choice_strict(raw, reference, truncated)
    return strict['outcome'] in ('correct', 'incorrect')


def score_code(raw, tests, imports=(), timeout=8, executor=execute):
    text = raw.strip()
    fences = re.findall(r'(?s)```(?:python)?\s*\n(.*?)\n```', text, flags=re.I)
    if fences:
        # Exactly one fenced block is unambiguous even with explanation around it; strict
        # code-only compliance is recorded separately by format_compliant().
        if len(fences) != 1:
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
