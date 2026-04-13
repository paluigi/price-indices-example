#!/usr/bin/env python3
"""Generate a large price/quantity dataset for bilateral price index benchmarking."""

import csv
import random

random.seed(42)

NUM_COMMON = 1200
NUM_ONLY_JAN = 150
NUM_ONLY_FEB = 150
RETAILERS = [1, 2]
MONTHS = ["2024-01-01", "2024-02-01"]

CATEGORIES = [
    ("Groceries", 1.0, 30.0, 10, 500),
    ("Electronics", 20.0, 500.0, 1, 50),
    ("Home goods", 5.0, 150.0, 5, 200),
    ("Clothing", 10.0, 200.0, 5, 100),
]

PRODUCT_NAMES = {
    "Groceries": [
        "Organic whole milk 1L",
        "Sourdough bread 500g",
        "Free-range eggs 12pk",
        "Cheddar cheese 250g",
        "Greek yogurt 500g",
        "Extra virgin olive oil 750ml",
        "Basmati rice 1kg",
        "Pasta penne 500g",
        "Canned tomatoes 400g",
        "Fresh salmon fillet 200g",
        "Chicken breast 500g",
        "Avocados 4pk",
        "Bananas 1kg",
        "Red apples 1kg",
        "Baby spinach 200g",
        "Dark chocolate 100g",
        "Instant coffee 200g",
        "Green tea bags 50pk",
        "Orange juice 1L",
        "Sparkling water 6pk",
        "Almond butter 350g",
        "Honey 500g",
        "Frozen peas 1kg",
        "Soy sauce 500ml",
        "Peanut butter 500g",
    ],
    "Electronics": [
        "USB-C cable 1m",
        "Wireless mouse",
        "Phone case",
        "Screen protector",
        "Power bank 10000mAh",
        "Bluetooth earbuds",
        "HDMI cable 2m",
        "Webcam 1080p",
        "USB hub 4-port",
        "SD card 64GB",
        "Wireless charger",
        "Portable speaker",
        "LED desk lamp",
        "Keyboard wrist rest",
        "Mouse pad XL",
    ],
    "Home goods": [
        "Cotton bath towel",
        "Kitchen sponge 3pk",
        "Trash bags 30L",
        "Dish soap 500ml",
        "Laundry detergent 1L",
        "Paper towels 4pk",
        "Candles scented set",
        "Picture frame A4",
        "Curtains blackout pair",
        "Pillow insert 50x70cm",
        "Cutting board bamboo",
        "Storage box 10L",
        "Clothes hangers 10pk",
        "Shower curtain",
        "Doormat 60x40cm",
    ],
    "Clothing": [
        "Cotton socks 3pk",
        "T-shirt plain",
        "Jeans slim fit",
        "Hoodie fleece",
        "Sneakers casual",
        "Belt leather",
        "Scarf wool blend",
        "Cap baseball",
        "Gloves winter",
        "Underwear briefs 3pk",
        "Polo shirt",
        "Jacket windbreaker",
        "Shorts chino",
        "Dress shirt slim",
        "Sweatpants joggers",
    ],
}


def gen_description(category, prod_num):
    names = PRODUCT_NAMES[category]
    return f"{names[prod_num % len(names)]} (variant {prod_num // len(names) + 1})"


def gen_row(prod_id, month, category, price_mean, price_std, qty_lo, qty_hi):
    price = round(random.gauss(price_mean, price_std * 0.15), 2)
    price = max(0.01, price)
    quantity = random.randint(qty_lo, qty_hi)
    desc = gen_description(category, prod_id)
    retailer = random.choice(RETAILERS)
    return {
        "time": month,
        "prices": price,
        "quantities": quantity,
        "prodID": prod_id,
        "retID": retailer,
        "description": desc,
    }


def main():
    rows = []
    next_id = 2001

    def assign_category(pid):
        return CATEGORIES[(pid - 2001) % len(CATEGORIES)]

    common_ids = list(range(next_id, next_id + NUM_COMMON))
    next_id += NUM_COMMON
    only_jan_ids = list(range(next_id, next_id + NUM_ONLY_JAN))
    next_id += NUM_ONLY_JAN
    only_feb_ids = list(range(next_id, next_id + NUM_ONLY_FEB))

    all_ids = common_ids + only_jan_ids + only_feb_ids

    for pid in common_ids:
        cat_name, p_mean, p_std, q_lo, q_hi = assign_category(pid)
        for month in MONTHS:
            for _ in RETAILERS:
                rows.append(gen_row(pid, month, cat_name, p_mean, p_std, q_lo, q_hi))

    for pid in only_jan_ids:
        cat_name, p_mean, p_std, q_lo, q_hi = assign_category(pid)
        for _ in RETAILERS:
            rows.append(gen_row(pid, MONTHS[0], cat_name, p_mean, p_std, q_lo, q_hi))

    for pid in only_feb_ids:
        cat_name, p_mean, p_std, q_lo, q_hi = assign_category(pid)
        for _ in RETAILERS:
            rows.append(gen_row(pid, MONTHS[1], cat_name, p_mean, p_std, q_lo, q_hi))

    random.shuffle(rows)

    out_path = "performance_price_data.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "time",
                "prices",
                "quantities",
                "prodID",
                "retID",
                "description",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    jan_prods = set(common_ids + only_jan_ids)
    feb_prods = set(common_ids + only_feb_ids)
    print(f"Written {len(rows)} rows to {out_path}")
    print(f"  Products in Jan only : {NUM_ONLY_JAN}")
    print(f"  Products in Feb only : {NUM_ONLY_FEB}")
    print(f"  Products in both     : {NUM_COMMON}")
    print(f"  Total unique products: {len(all_ids)}")


if __name__ == "__main__":
    main()
