from collections import defaultdict, Counter
from itertools import combinations

class FPNode:
    def __init__(self, item, parent):
        self.item = item
        self.count = 1
        self.parent = parent
        self.children = {}
        self.link = None

    def increment(self, count=1):
        self.count += count


class BasketLift:
    def __init__(self, min_support=2, min_confidence=0.5, min_lift=1.0):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.min_lift = min_lift
        self.frequent_itemsets = {}
        self.rules = []

    def preprocess(self, transactions):
        item_counts = Counter()
        for transaction in transactions:
            item_counts.update(transaction)

        items_above_support = {item for item, count in item_counts.items() if count >= self.min_support}
        reordered = []
        for transaction in transactions:
            filtered = [item for item in transaction if item in items_above_support]
            sorted_items = sorted(filtered, key=lambda item: (-item_counts[item], item))
            if sorted_items:
                reordered.append(sorted_items)

        return reordered, item_counts

    def build_tree(self, transactions):
        root = FPNode(None, None)
        header_table = {}

        for transaction in transactions:
            current_node = root
            for item in transaction:
                if item in current_node.children:
                    current_node.children[item].increment()
                else:
                    new_node = FPNode(item, current_node)
                    current_node.children[item] = new_node
                    if item in header_table:
                        last_node = header_table[item]
                        while last_node.link:
                            last_node = last_node.link
                        last_node.link = new_node
                    else:
                        header_table[item] = new_node
                current_node = current_node.children[item]
        return root, header_table

    def ascend_tree(self, node):
        path = []
        while node.parent and node.parent.item is not None:
            node = node.parent
            path.append(node.item)
        return path[::-1]

    def find_prefix_paths(self, base_item, node):
        paths = []
        while node:
            path = self.ascend_tree(node)
            if path:
                paths.append((path, node.count))
            node = node.link
        return paths

    def mine_tree(self, header_table, prefix):
        items = sorted(header_table.items(), key=lambda x: x[1].count)
        for item, node in items:
            new_pattern = prefix + [item]
            support = 0
            temp_node = node
            while temp_node:
                support += temp_node.count
                temp_node = temp_node.link
            if support >= self.min_support:
                self.frequent_itemsets[tuple(new_pattern)] = support
                conditional_patterns = self.find_prefix_paths(item, node)
                conditional_transactions = []
                for path, count in conditional_patterns:
                    conditional_transactions.extend([path] * count)
                if conditional_transactions:
                    cond_tree, cond_header = self.build_tree(conditional_transactions)
                    self.mine_tree(cond_header, new_pattern)

    def fit(self, transactions):
        transactions, _ = self.preprocess(transactions)
        tree, header_table = self.build_tree(transactions)
        self.mine_tree(header_table, [])
        self.generate_rules()

    def generate_rules(self):
        total_supports = sum(self.frequent_itemsets.values())

        for itemset in self.frequent_itemsets:
            if len(itemset) < 2:
                continue
            itemset_support = self.frequent_itemsets[itemset]
            for i in range(1, len(itemset)):
                for antecedent in combinations(itemset, i):
                    antecedent = tuple(sorted(antecedent))
                    consequent = tuple(sorted(set(itemset) - set(antecedent)))
                    if not consequent:
                        continue
                    antecedent_support = self.frequent_itemsets.get(antecedent)
                    consequent_support = self.frequent_itemsets.get(consequent)
                    if not antecedent_support or not consequent_support:
                        continue
                    confidence = itemset_support / antecedent_support
                    lift = confidence / (consequent_support / total_supports)
                    if confidence >= self.min_confidence and lift >= self.min_lift:
                        self.rules.append({
                            'antecedent': antecedent,
                            'consequent': consequent,
                            'support': itemset_support,
                            'confidence': round(confidence, 3),
                            'lift': round(lift, 3)
                        })

    def print_rules(self):
        for rule in self.rules:
            a = ', '.join(rule['antecedent'])
            c = ', '.join(rule['consequent'])
            print(f"If a customer buys [{a}], they also buy [{c}] "
                  f"(Support: {rule['support']}, Confidence: {rule['confidence']*100:.1f}%, Lift: {rule['lift']})")
