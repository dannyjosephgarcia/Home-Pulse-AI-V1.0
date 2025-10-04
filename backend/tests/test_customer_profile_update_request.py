import unittest
from backend.db.model.customer_profile_update_request import CustomerProfileUpdateRequest
from backend.db.model.billing_plans import BillingPlans
from common.logging.error.error import Error


class TestCustomerProfileUpdateRequest(unittest.TestCase):

    def test_valid_request_with_all_fields(self):
        """Test creating a valid CustomerProfileUpdateRequest with all fields"""
        request = {
            'firstName': 'John',
            'lastName': 'Doe',
            'billingPlanType': 'YEARLY'
        }

        obj = CustomerProfileUpdateRequest(request)

        self.assertEqual(obj.first_name, 'John')
        self.assertEqual(obj.last_name, 'Doe')
        self.assertEqual(obj.billing_plan_type, 'YEARLY')

    def test_valid_request_with_only_first_name(self):
        """Test creating a valid CustomerProfileUpdateRequest with only firstName"""
        request = {
            'firstName': 'Jane'
        }

        obj = CustomerProfileUpdateRequest(request)

        self.assertEqual(obj.first_name, 'Jane')
        self.assertIsNone(obj.last_name)
        self.assertIsNone(obj.billing_plan_type)

    def test_valid_request_with_only_last_name(self):
        """Test creating a valid CustomerProfileUpdateRequest with only lastName"""
        request = {
            'lastName': 'Smith'
        }

        obj = CustomerProfileUpdateRequest(request)

        self.assertIsNone(obj.first_name)
        self.assertEqual(obj.last_name, 'Smith')
        self.assertIsNone(obj.billing_plan_type)

    def test_valid_request_with_only_billing_plan(self):
        """Test creating a valid CustomerProfileUpdateRequest with only billingPlanType"""
        request = {
            'billingPlanType': 'MONTHLY'
        }

        obj = CustomerProfileUpdateRequest(request)

        self.assertIsNone(obj.first_name)
        self.assertIsNone(obj.last_name)
        self.assertEqual(obj.billing_plan_type, 'MONTHLY')

    def test_empty_request(self):
        """Test creating CustomerProfileUpdateRequest with empty request"""
        request = {}

        obj = CustomerProfileUpdateRequest(request)

        self.assertIsNone(obj.first_name)
        self.assertIsNone(obj.last_name)
        self.assertIsNone(obj.billing_plan_type)

    def test_first_name_not_string(self):
        """Test that Error is raised when firstName is not a string"""
        request = {
            'firstName': 12345
        }

        with self.assertRaises(Error):
            CustomerProfileUpdateRequest(request)

    def test_last_name_not_string(self):
        """Test that lastName not being string is handled (logs but doesn't raise)"""
        request = {
            'lastName': 12345
        }

        # Note: Current implementation logs error but doesn't raise
        obj = CustomerProfileUpdateRequest(request)
        self.assertEqual(obj.last_name, 12345)

    def test_billing_plan_type_not_string(self):
        """Test that Error is raised when billingPlanType is not a string"""
        request = {
            'billingPlanType': 12345
        }

        with self.assertRaises(Error):
            CustomerProfileUpdateRequest(request)

    def test_invalid_billing_plan_type(self):
        """Test that Error is raised when billingPlanType is invalid"""
        request = {
            'billingPlanType': 'INVALID_PLAN'
        }

        with self.assertRaises(Error):
            CustomerProfileUpdateRequest(request)

    def test_yearly_billing_plan(self):
        """Test that YEARLY billing plan is accepted"""
        request = {
            'billingPlanType': BillingPlans.YEARLY.value
        }

        obj = CustomerProfileUpdateRequest(request)
        self.assertEqual(obj.billing_plan_type, 'YEARLY')

    def test_monthly_billing_plan(self):
        """Test that MONTHLY billing plan is accepted"""
        request = {
            'billingPlanType': BillingPlans.MONTHLY.value
        }

        obj = CustomerProfileUpdateRequest(request)
        self.assertEqual(obj.billing_plan_type, 'MONTHLY')


if __name__ == '__main__':
    unittest.main()
