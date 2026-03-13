import unittest
from unittest.mock import Mock

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError
from src.checkout import CheckoutService, ChargeResult

class TestCheckoutService(unittest.TestCase):
	
	def setUp(self):
		super().setUp()
		self.payments = Mock()
		self.email = Mock()
		self.fraud = Mock()
		self.repo = Mock()
		self.pricing = Mock()

		self.payments.charge.return_value = ChargeResult(True, "1")
		self.email.charge.return_value = None
		self.fraud.score.return_value = 0
		self.repo.save.return_value = None
		self.pricing.total_cents.return_value = 12000

		self.items = [CartItem("1", 5000, 2), CartItem("2", 2000, 1)]

		self.checkout = CheckoutService(
			payments=self.payments,
			email=self.email,
			fraud=self.fraud,
			repo=self.repo,
			pricing=self.pricing,
		)

	def test_checkout_successful(self):
		assert "OK:" in self.checkout.checkout("1", self.items, "token", "CL", "")

	def test_checkout_fail_if_no_user(self):
		assert self.checkout.checkout(" ", self.items, "token", "CL", "") == "INVALID_USER"

	def test_checkout_fail_if_pricing_error(self):
		self.pricing.total_cents.side_effect = PricingError()

		assert self.checkout.checkout("1", self.items, "token", "CL", "") == f"INVALID_CART:{PricingError()}"

	def test_checkout_fail_if_high_fraud_score(self):
		self.fraud.score.return_value = 80

		assert self.checkout.checkout("1", self.items, "token", "CL", "") == "REJECTED_FRAUD"

	def test_checkout_fail_if_payment_failed(self):
		self.payments.charge.return_value = ChargeResult(False, "1", "Error")

		assert self.checkout.checkout("1", self.items, "token", "CL", "") == f"PAYMENT_FAILED:Error"

	def test_checkout_integrates_with_pricing_service(self):
		self.checkout = CheckoutService(
			payments=self.payments,
			email=self.email,
			fraud=self.fraud,
			repo=self.repo,
			pricing=PricingService(),
		)

		assert "OK:" in self.checkout.checkout("1", self.items, "token", "CL", "")
