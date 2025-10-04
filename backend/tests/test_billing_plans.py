import unittest
from backend.db.model.billing_plans import BillingPlans


class TestBillingPlans(unittest.TestCase):

    def test_billing_plans_enum_values(self):
        """Test that BillingPlans enum has the correct values"""
        self.assertEqual(BillingPlans.YEARLY.value, 'YEARLY')
        self.assertEqual(BillingPlans.MONTHLY.value, 'MONTHLY')

    def test_billing_plans_enum_members(self):
        """Test that BillingPlans has exactly two members"""
        members = list(BillingPlans)
        self.assertEqual(len(members), 2)
        self.assertIn(BillingPlans.YEARLY, members)
        self.assertIn(BillingPlans.MONTHLY, members)

    def test_billing_plans_uniqueness(self):
        """Test that BillingPlans values are unique"""
        values = [plan.value for plan in BillingPlans]
        self.assertEqual(len(values), len(set(values)))

    def test_billing_plans_access_by_name(self):
        """Test accessing BillingPlans by name"""
        self.assertEqual(BillingPlans['YEARLY'], BillingPlans.YEARLY)
        self.assertEqual(BillingPlans['MONTHLY'], BillingPlans.MONTHLY)

    def test_billing_plans_access_by_value(self):
        """Test accessing BillingPlans by value"""
        self.assertEqual(BillingPlans('YEARLY'), BillingPlans.YEARLY)
        self.assertEqual(BillingPlans('MONTHLY'), BillingPlans.MONTHLY)


if __name__ == '__main__':
    unittest.main()
