import logging
from common.logging.log_utils import START_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INVALID_REQUEST
from backend.db.model.billing_plans import BillingPlans


class CustomerProfileUpdateRequest:
    def __init__(self, request):
        self._validate_customer_profile_update_request(request)
        self.first_name = request.get('firstName')
        self.last_name = request.get('lastName')
        self.billing_plan_type = request.get('billingPlanType')

    @staticmethod
    def _validate_customer_profile_update_request(request):
        """
        Validates request to the PUT route for customer profiles
        :param request: The request for the route
        :return:
        """
        logging.info(START_OF_METHOD)
        if 'firstName' in request:
            if not isinstance(request['firstName'], str):
                logging.error('The firstName field must be a string')
                raise Error(INVALID_REQUEST)
        if 'lastName' in request:
            if not isinstance(request['lastName'], str):
                logging.error('The lastName field must be a string')
        if 'billingPlanType' in request:
            if not isinstance(request['billingPlanType'], str):
                logging.error('The billingPlanType field must be a string')
                raise Error(INVALID_REQUEST)
            if request['billingPlanType'] not in [BillingPlans.YEARLY.value, BillingPlans.MONTHLY.value]:
                logging.error('Invalid billingPlanType')
                raise Error(INVALID_REQUEST)
