import unittest
from unittest.mock import Mock

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError

class TestPricingService(unittest.TestCase):

	service = PricingService()

	def test_subtotal_add_prices(self):
		items = [CartItem("1", 160, 2), CartItem("2", 55, 1)]
		assert self.service.subtotal_cents(items) == 375

	def test_subtotal_error_if_price_negative(self):
		items = [CartItem("1", -160, 2), CartItem("2", 55, 1)]
		with self.assertRaises(PricingError):
			self.service.subtotal_cents(items)

	def test_subtotal_error_if_quantity_zero(self):
		items = [CartItem("1", 160, 0), CartItem("2", 55, 1)]
		with self.assertRaises(PricingError):
			self.service.subtotal_cents(items)

	def test_apply_coupon_no_coupon(self):
		assert self.service.apply_coupon(100, None) == 100

	def test_apply_coupon_empty_coupon(self):
		assert self.service.apply_coupon(100, "") == 100

	def test_apply_coupon_spaces_coupon(self):
		assert self.service.apply_coupon(100, "  ") == 100

	def test_apply_coupon_SAVE10(self):
		assert self.service.apply_coupon(100, "SAVE10") == 90
	
	def test_apply_coupon_CLP2000(self):
		assert self.service.apply_coupon(10000, "CLP2000") == 8000

	def test_apply_coupon_error_invalid(self):
		with self.assertRaises(PricingError):
			self.service.apply_coupon(100, "not a coupon")

	def test_tax_chile(self):
		assert self.service.tax_cents(100, "CL") == 19

	def test_tax_usa(self):
		assert self.service.tax_cents(100, "US") == 0

	def test_tax_eu(self):
		assert self.service.tax_cents(100, "EU") == 21

	def test_tax_ignore_capitalization_and_spaces(self):
		assert self.service.tax_cents(100, " cL  ") == 19

	def test_tax_error_unsupported_country(self):
		with self.assertRaises(PricingError):
			self.service.tax_cents(100, "Not A Country")

	def test_shipping_chile_under_20000_default(self):
		assert self.service.shipping_cents(100, "CL") == 2500
	
	def test_shipping_chile_20000_free(self):
		assert self.service.shipping_cents(20000, "CL") == 0

	def test_shipping_chile_over_20000_free(self):
		assert self.service.shipping_cents(25000, "CL") == 0

	def test_shipping_usa(self):
		assert self.service.shipping_cents(25000, "US") == 5000

	def test_shipping_eu(self):
		assert self.service.shipping_cents(25000, "EU") == 5000

	def test_shipping_error_unsupported_country(self):
		with self.assertRaises(PricingError):
			self.service.shipping_cents(25000, "Not A Country")

	def test_calculate_total(self):
		items = [CartItem("1", 5000, 2), CartItem("2", 2000, 1)]
		assert self.service.total_cents(items, "CLP2000", "EU") == 17100
