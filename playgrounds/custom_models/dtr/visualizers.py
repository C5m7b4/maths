import graphviz


def visualize_tree_pdf(tree, feature_names=None, depth=0, node_id=0, dot=None):
    if dot is None:
        dot = graphviz.Digraph()
        dot.node(str(node_id), label="Root")

    current_node_id = node_id

    if isinstance(tree, dict):
        feat = tree['feature']
        thresh = tree['threshold']
        feat_name = feature_names[feat] if feature_names else f"X[{feat}]"
        label = f"{feat_name} <= {thresh:.2f}"
        left_id = current_node_id * 2 + 1
        right_id = current_node_id * 2 + 2

        dot.node(str(left_id), label="")
        dot.node(str(right_id), label="")

        dot.edge(str(current_node_id), str(left_id), label="yes")
        dot.edge(str(current_node_id), str(right_id), label="no")

        dot.node(str(current_node_id), label=label)

        visualize_tree_pdf(tree['left'], feature_names, depth + 1, left_id, dot)
        visualize_tree_pdf(tree['right'], feature_names, depth + 1, right_id, dot)
    else:
        label = f"Predict: {tree:.2f}"
        dot.node(str(current_node_id), label=label)

    return dot

def visualize_tree_basic(node, depth=0, feature_names=None):
    indent = "  " * depth
    if not isinstance(node, dict):
        print(f"{indent}Predict: {node:.2f}")
    else:
        feat_name = f"feature_{node['feature']}"
        if feature_names:
            feat_name = feature_names[node['feature']]
        threshold = node['threshold']
        print(f"{indent}if {feat_name} <= {threshold:.2f}:")
        visualize_tree_basic(node['left'], depth + 1, feature_names)
        print(f"{indent}else:  # {feat_name} > {threshold:.2f}")
        visualize_tree_basic(node['right'], depth + 1, feature_names)