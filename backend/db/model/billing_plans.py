from enum import Enum, unique


@unique
class BillingPlans(Enum):
    YEARLY = 'YEARLY'
    MONTHLY = 'MONTHLY'
