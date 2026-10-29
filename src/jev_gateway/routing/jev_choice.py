"""Jev typed choice among the currently eligible generation backends."""
from .contracts import Decision, RoutingError, RoutingRequest


class JevChoiceRouter:
    name = 'jev-choice'
    version = '1'
    question_version = 'routing-choice-v1'

    def __init__(self, settings, client):
        self.settings = settings
        self.client = client

    async def decide(self, request: RoutingRequest) -> Decision:
        if not request.eligible_tiers:
            raise RoutingError('no eligible generator for Jev choice')
        criteria = {tier: f'{tier} generation backend; configured model {self.settings.backend(tier).model}; '
                          f'context limit {self.settings.backend(tier).max_context_tokens} tokens'
                    for tier in request.eligible_tiers}
        question = {'type':'choice',
                    'instructions':'Choose the least costly eligible backend likely to answer this user request correctly. '
                                   'This selects a generation backend; it does not verify an answer.',
                    'criteria':criteria}
        reply = await self.client.decide(
            {'messages':request.messages, 'question_version':self.question_version,
             'generation_settings':request.settings_fingerprint}, {'route':question})
        try:
            answer = reply.answers['route']
            selected = answer['choice']
            probabilities = answer['probabilities']
            if (answer['type'] != 'choice' or selected not in request.eligible_tiers or
                set(probabilities) != set(request.eligible_tiers) or
                any(not isinstance(p,(float,int)) or not 0 <= p <= 1 for p in probabilities.values()) or
                abs(sum(probabilities.values())-1) > .02):
                raise ValueError('invalid choice probabilities or tier')
        except (KeyError, TypeError, ValueError) as exc:
            raise RoutingError('Jev choice answer invalid') from exc
        return Decision(selected, self.name, self.version, reply.duration_ms,
                        request_id=request.request_id, settings_fingerprint=request.settings_fingerprint,
                        probability_event='Jev routing choice among eligible tiers',
                        probabilities=probabilities, usage=reply.usage,
                        question_version=self.question_version, decision_model=reply.model,
                        raw_value=selected)
