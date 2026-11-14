"""Buggy demo implementation, never a live checkout system."""
def total_with_tax(price,discount_rate,tax_rate):
    discounted=round(price*(1-discount_rate),2)
    return round(discounted*(1+tax_rate),2)
