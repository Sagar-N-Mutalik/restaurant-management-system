"""
Strategy Design Pattern Implementation

Pattern Goal: Define a family of algorithms, encapsulate each one, and make them interchangeable.
Strategy lets the algorithm vary independently from clients that use it.

Real-world Problem Solved:
A restaurant needs different pricing rules (normal pricing, happy hour, VIP discounts). 
Without Strategy, the Order processing or checkout logic would be filled with massive 
`if/else` or `switch` statements checking the current time or customer status. As new 
promotions are added, this file would grow endlessly and violate the Open/Closed Principle.

How it implements the pattern:
The `PricingStrategy` interface defines an abstract `calculate_final_price` method. The concrete 
strategies (`NormalPricing`, `HappyHourPricing`, `VIPDiscountPricing`) each implement this method 
with specific mathematical logic. The context (in our case, the Facade) holds a reference to a 
`PricingStrategy` object and delegates the calculation to it instead of doing it inline. The system 
can switch between these strategies dynamically at runtime based on the client's HTTP request.
"""

from abc import ABC, abstractmethod

class PricingStrategy(ABC):
    """
    The Strategy interface declaring operations common to all supported versions
    of some algorithm (pricing calculation in our case).
    """
    @abstractmethod
    def calculate_final_price(self, base_price: float) -> float:
        pass

    def apply_gst(self, amount: float) -> float:
        """
        Calculates the 18% GST on top of the provided amount.
        Returns the finalized total amount after taxes natively.
        """
        return float(amount) * 1.18


class NormalPricing(PricingStrategy):
    """
    Concrete Strategy representing standard pricing with no special discounts.
    """
    def calculate_final_price(self, base_price: float) -> float:
        return float(base_price)


class HappyHourPricing(PricingStrategy):
    """
    Concrete Strategy representing Happy Hour pricing, e.g., applying a 20% discount.
    """
    def calculate_final_price(self, base_price: float) -> float:
        return float(base_price) * 0.8  # 20% Off


class VIPDiscountPricing(PricingStrategy):
    """
    Concrete Strategy for VIP members, applying a flat discount or customized rate.
    """
    def __init__(self, vip_discount_rate=0.7):
        # Allow customizable VIP rates, default to 30% off (pay 70%)
        self.vip_discount_rate = vip_discount_rate

    def calculate_final_price(self, base_price: float) -> float:
        return float(base_price) * self.vip_discount_rate
