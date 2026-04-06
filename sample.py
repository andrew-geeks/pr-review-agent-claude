def calculate_total(price, quantity):
    return price * quantity


def get_discount(total):
    if total > 100:
        return total * 0.1
    return 0


def apply_discount(price, quantity):
    total = calculate_total(price, quantity)
    discount = get_discount(total)
    return total - discount


def process_order(items):
    grand_total = 0
    for item in items:
        grand_total += apply_discount(item["price"], item["quantity"])
    return grand_total
