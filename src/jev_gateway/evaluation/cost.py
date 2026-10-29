"""Cost states are explicit; missing usage/rates remain unknown."""
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ApiRate:
    model: str
    input_usd_per_million: float
    output_usd_per_million: float
    effective_date: date
    source_url: str

    def __post_init__(self):
        if min(self.input_usd_per_million,self.output_usd_per_million)<0 or not self.source_url.startswith('https://'):
            raise ValueError('nonnegative rates and source URL required')


def account_attempts(attempts, rate=None):
    charges=[]
    for attempt in attempts:
        if attempt.charge_usd is not None:
            charges.append(('known_charge',attempt.charge_usd))
        elif rate and attempt.prompt_tokens is not None and attempt.completion_tokens is not None:
            amount=(attempt.prompt_tokens*rate.input_usd_per_million+attempt.completion_tokens*rate.output_usd_per_million)/1e6
            charges.append(('estimated_api',amount))
        else:
            charges.append(('unknown',None))
    if not charges or any(status=='unknown' for status,_ in charges):
        return {'status':'unknown','charge_usd':None,'attempt_count':len(attempts)}
    return {'status':'known_charge' if all(status=='known_charge' for status,_ in charges) else 'estimated_api','charge_usd':sum(value for _,value in charges),'attempt_count':len(attempts)}


def capacity_cost(hourly_usd, allocated_hours, busy_hours):
    if min(hourly_usd,allocated_hours,busy_hours)<0 or busy_hours>allocated_hours:
        raise ValueError('invalid capacity inputs')
    return {'status':'modeled_capacity','charge_usd':hourly_usd*allocated_hours,'idle_hours':allocated_hours-busy_hours}


def attach_cost(result, rate=None):
    if rate is not None and rate.model != result.model:
        raise ValueError('rate model does not match observed model')
    accounting=account_attempts(result.attempts,rate)
    return result.model_copy(update={'cost_status':accounting['status'],'charge_usd':accounting['charge_usd']})
