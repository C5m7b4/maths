import random
import pandas as pd

def generate_transactions(base_items, dtc=10, max_items=8, mqpi=10, minia=.99, maxia=5.99):
    """Generate a random set of transactions using a base dataset of items to choose from.
    
    Args:
        base_items (list): list containing the base dataset of items.
        dtc (int): Desired Transaction Count - Number of transactions to generate.
        max_items (int): Maximum number of items per transaction.
        mqpi (int): Maximum quantity per item.
        minia (float): Minimum item price for each item.
        maxia (float): Maximum item price for each item.

    """

    transaction_list = []
    for tx_id in range(1, dtc + 1):
        num_items = random.randint(1,max_items)

        for _ in range(num_items):
            item = random.choice(base_items)
            qty = random.randint(1, mqpi)
            price_per_unit = round(random.uniform(minia, maxia), 2)
            sales = round(qty * price_per_unit, 2)

            transaction_list.append({
                'transaction_id': tx_id,
                'product_code': item['product_code'],
                'product_description': item['product_description'],
                'qty': qty,
                'price_per_unit': price_per_unit,
                'sales': sales
            })
    return pd.DataFrame(transaction_list)