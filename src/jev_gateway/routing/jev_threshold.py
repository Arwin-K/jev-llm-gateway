"""Jev Noul questions about generator success, with validation-selected thresholds."""
from .contracts import Decision, RoutingError, RoutingRequest, TIERS


class JevThresholdRouter:
    name = 'jev-threshold'
    version = '1'
    question_version = 'generator-success-v1'

    def __init__(self, settings, client, thresholds: dict[str, float], *, selection_id: str):
        if not selection_id or set(thresholds) != set(TIERS) or any(not 0 <= x <= 1 for x in thresholds.values()):
            raise ValueError('thresholds for every tier and validation selection ID required')
        self.settings = settings
        self.client = client
        self.thresholds = thresholds
        self.selection_id = selection_id

    async def decide(self, request: RoutingRequest) -> Decision:
        if not request.eligible_tiers:
            raise RoutingError('no eligible generator for Jev success questions')
        questions = {tier: {'type':'noul',
                            'instructions':f'Will the configured {tier} generator ({self.settings.backend(tier).model}) '
                                           'produce a correct answer to this exact request under the stated output limit? '
                                           'True means the externally scored answer is correct; false includes incorrect '
                                           'or unparsable answers.'}
                     for tier in request.eligible_tiers}
        reply = await self.client.decide(
            {'messages':request.messages, 'max_output_tokens':request.max_output_tokens,
             'question_version':self.question_version, 'generation_settings':request.settings_fingerprint},
            questions)
        try:
            probabilities = {tier: reply.answers[tier]['noul'] for tier in request.eligible_tiers}
            if any(reply.answers[tier]['type'] != 'noul' or
                   not isinstance(probabilities[tier], (float,int)) or
                   not 0 <= probabilities[tier] <= 1 for tier in probabilities):
                raise ValueError('invalid success probability')
        except (KeyError, TypeError, ValueError) as exc:
            raise RoutingError('Jev success answer invalid') from exc
        tier = next((candidate for candidate in TIERS if candidate in probabilities and
                     probabilities[candidate] >= self.thresholds[candidate]), None)
        if tier is None:
            raise RoutingError('no eligible tier cleared its success threshold')
        return Decision(tier, self.name, self.version, reply.duration_ms,
                        request_id=request.request_id, settings_fingerprint=request.settings_fingerprint,
                        probability_event='specified generator answer externally scores correct',
                        probabilities=probabilities, usage=reply.usage,
                        question_version=self.question_version, decision_model=reply.model,
                        raw_value=probabilities[tier])
