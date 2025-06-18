import numpy as np
from collections import Counter
import graphviz

class DecisionTreeRegressor:
    def __init__(self, max_depth=None, min_sample_split=2):
        self.max_depth = max_depth
        self.min_sample_split = min_sample_split
        print(f'DecisionTreeRegressor initialized with max_depth={max_depth}, min_sample_split={min_sample_split}')
        self.tree = None
    
    def report(self):
        print(f'max_depth: {self.max_depth}')
        print(f'self.tree={self.tree}')

    def fit(self, X, y):
        print(f'Fitting DecisionTreeRegressor...')
        print(f'\tX shape: {X.shape}, y shape: {y.shape}')
        print(f'\tX:\n\t{X[:5]}')
        print(f'\ty:\n\t{y[:5]}')
        self.tree = self._build_tree(X, y)

    def predict(self, X):
        result = np.array([self._predict_sample(x, self.tree) for x in X])
        print(f'predict, result shape: {result.shape}')
        return result
    
    def _build_tree(self, X, y, depth=0):
        num_samples, num_features = X.shape
        print(f'Building tree at depth {depth}, num_samples(rows): {num_samples}, num_features(columns): {num_features}')
        if (self.max_depth is not None and depth >= self.max_depth) or num_samples < self.min_sample_split:
            print(f'🧙Reached leaf node at depth {depth}, returning mean value: {np.mean(y)}')
            return np.mean(y)
        
        best_feat, best_thresh = self._best_split(X, y)
        if best_feat is None:
            return np.mean(y)
        
        left_mask = X[:, best_feat] <= best_thresh
        right_mask = X[:, best_feat] > best_thresh

        left = self._build_tree(X[left_mask], y[left_mask], depth + 1)
        right = self._build_tree(X[right_mask], y[right_mask], depth + 1)

        print(f'Split on feature {best_feat} at threshold {best_thresh}')
        return {'feature': best_feat, 'threshold': best_thresh, 'left': left, 'right': right}
    
    def _best_split(self, X, y):
        print('******** Checking for best split...')
        best_mse = float('inf')
        best_feat, best_thresh = None, None

        for feat in range(X.shape[1]):
            thresholds = np.unique(X[:, feat])
            print(f'\tFeature {feat}, thresholds(values): {thresholds}')
            for t in thresholds:
                print(f'\t\tEvaluating feature {feat} at threshold {t}  ')
                left_mask = X[:, feat] <= t
                right_mask = X[:, feat] > t

                masked_l = y[left_mask]
                masked_r = y[right_mask]
                print(f'\t\tLeft mask count: {len(masked_l)}, Right mask count: {len(masked_r)}')
                if len(masked_l) == 0 or len(masked_r) == 0:
                    continue

                mse = self._calculate_mse(masked_l, masked_r)
                if mse < best_mse:
                    best_mse = mse
                    best_feat = feat
                    best_thresh = t

        print(f'Best feature to split on: {best_feat} at threshold {best_thresh} with MSE: {best_mse}')
        return best_feat, best_thresh
    
    def _calculate_mse(self, left_y, right_y):
        left_mse = np.var(left_y) * len(left_y)
        right_mse = np.var(right_y) * len(right_y)
        result =  (left_mse + right_mse) / (len(left_y) + len(right_y))
        print(f'\t\tLeft MSE: {left_mse}, Right MSE: {right_mse}, len(left): {len(left_y)}, len(right): {len(right_y)}  result: {result}')
        return result
    
    def _predict_sample(self, x, node):
        if not isinstance(node, dict):
            return node
        print(f'checking prediction At node: {node}, sample value: {x[node['feature']]}'    )
        if x[node['feature']] <= node['threshold']:
            return self._predict_sample(x, node['left'])
        else:
            return self._predict_sample(x, node['right'])
        

        


class RandomForestRegressorFromScratch:
    def __init__(self, n_estimators=10, max_depth=None, min_samples_split=2, max_features='sqrt'):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features
        self.trees = []
        self.feature_subsets = []
        print('RandomForestRegressorFromScratch initialized')

    def _get_feature_indices(self, n_features):
        print(f'get_feature_indices, n_features: {n_features}')
        if self.max_features == 'sqrt':
            return np.random.choice(n_features, int(np.sqrt(n_features)), replace=False)
        elif isinstance(self.max_features, int):
            return np.random.choice(n_features, self.max_features, replace=False)
        else:
            return np.arange(n_features)

    def fit(self, X, y):
        print('Fitting RandomForestRegressorFromScratch...')
        self.trees = []
        self.feature_subsets = []

        for _ in range(self.n_estimators):
            # Bootstrap sample
            indices = np.random.choice(len(X), len(X), replace=True)
            print(f'Bootstrap sample indices: {indices}')
            X_sample, y_sample = X[indices], y[indices]
            print(f'X_sample shape: {X_sample.shape}, y_sample shape: {y_sample.shape}')

            # Feature subset
            feature_idx = self._get_feature_indices(X.shape[1])
            print(f'Feature indices for this tree: {feature_idx}')
            self.feature_subsets.append(feature_idx)

            # Train tree
            tree = DecisionTreeRegressor(
                max_depth=self.max_depth,
                min_sample_split=self.min_samples_split
            )
            tree.fit(X_sample[:, feature_idx], y_sample)
            print(f'Tree trained with feature indices: {feature_idx}')
            self.trees.append(tree)

    def predict(self, X):
        preds = np.array([
            tree.predict(X[:, feat_idx]) for tree, feat_idx in zip(self.trees, self.feature_subsets)
        ])
        print(f'Predictions from all trees shape: {preds.shape}')
        return np.mean(preds, axis=0)

    def feature_importances_(self, feature_names):
        # Count how often features were used across trees
        importances = Counter()
        total_splits = 0

        for tree, feat_idx in zip(self.trees, self.feature_subsets):
            stack = [tree.tree]
            while stack:
                node = stack.pop()
                if isinstance(node, dict):
                    importances[feature_names[feat_idx[node['feature']]]] += 1
                    total_splits += 1
                    stack.extend([node['left'], node['right']])

        # Normalize
        print(f'Total splits across all trees: {total_splits}')
        return {feat: count / total_splits for feat, count in importances.items()}

X_small = np.array([
    [1, 10],   # A
    [2, 20],   # B
    [3, 30],   # C
    [4, 40],   # D
    [5, 50]    # E
])
y_small = np.array([100, 200, 300, 400, 500]) 

debug_tree = DecisionTreeRegressor(max_depth=2)
debug_tree.fit(X_small, y_small)
debug_tree.report()

# Define visualization function
# def visualize_tree(node, depth=0, feature_names=None):
#     indent = "  " * depth
#     if not isinstance(node, dict):
#         print(f"{indent}Predict: {node:.2f}")
#     else:
#         feat_name = f"feature_{node['feature']}"
#         if feature_names:
#             feat_name = feature_names[node['feature']]
#         threshold = node['threshold']
#         print(f"{indent}if {feat_name} <= {threshold:.2f}:")
#         visualize_tree(node['left'], depth + 1, feature_names)
#         print(f"{indent}else:  # {feat_name} > {threshold:.2f}")
#         visualize_tree(node['right'], depth + 1, feature_names)

#visualize_tree(debug_tree.tree, feature_names=["feature_0", "feature_1"])        

# def visualize_tree_pdf(tree, feature_names=None, depth=0, node_id=0, dot=None):
#     if dot is None:
#         dot = graphviz.Digraph()
#         dot.node(str(node_id), label="Root")

#     current_node_id = node_id

#     if isinstance(tree, dict):
#         feat = tree['feature']
#         thresh = tree['threshold']
#         feat_name = feature_names[feat] if feature_names else f"X[{feat}]"
#         label = f"{feat_name} <= {thresh:.2f}"
#         left_id = current_node_id * 2 + 1
#         right_id = current_node_id * 2 + 2

#         dot.node(str(left_id), label="")
#         dot.node(str(right_id), label="")

#         dot.edge(str(current_node_id), str(left_id), label="yes")
#         dot.edge(str(current_node_id), str(right_id), label="no")

#         dot.node(str(current_node_id), label=label)

#         visualize_tree_pdf(tree['left'], feature_names, depth + 1, left_id, dot)
#         visualize_tree_pdf(tree['right'], feature_names, depth + 1, right_id, dot)
#     else:
#         label = f"Predict: {tree:.2f}"
#         dot.node(str(current_node_id), label=label)

#     return dot

# feature_names = ['Feature 1', 'Feature 2']
# tree_graph = visualize_tree_pdf(debug_tree.tree, feature_names)
# tree_graph.render('debug_decision_tree', format='pdf', cleanup=False)