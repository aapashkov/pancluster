# %%
import sys

import numpy as np
import pandas as pd
from sklearn import (
    ensemble,
    feature_selection,
    model_selection,
    pipeline,
    preprocessing
)

# %%
pangenome = pd.read_csv(
    "data/pangenome/pangenome.full.tsv", sep="\t", index_col="genome"
)
pangenome

# %%
target = pd.read_csv("accessions.tsv", sep="\t", index_col="genome")["fsp"]
target

# %%
def logstep(start: int, end: int, step: float):
    # logstep(10, 1200, 1) -> 10 100 1000 1200
    steps = []
    current = start
    power = 1
    while current < end:
        steps.append(current)
        power += step
        current = round(start**power)
    steps.append(end)
    return steps

# %%
def random_feature_names(
    transformer: preprocessing.FunctionTransformer,
    input_features: np.ndarray
):
    default = {"seed": 0, "size": 10}
    passed = transformer.get_params()["kw_args"]
    args = default if passed is None else {**default, **passed}
    seed = args["seed"]
    size = args["size"]
    selection = np.random.default_rng(seed + size).choice(
        input_features.shape[0], size, replace=False
    )
    return input_features[selection]

def random_selector(X: np.ndarray, seed: int = 0, size: int = 10):
    selection = np.random.default_rng(seed + size).choice(
        X.shape[1], size, replace=False
    )
    return X[:, selection]

RandomSelector = preprocessing.FunctionTransformer(
    random_selector,
    validate=True,
    feature_names_out=random_feature_names,
    kw_args={"seed": 10}
)
RandomSelector

# %%
def run_search(
    dataframe: pd.DataFrame,
    target: pd.Series,
    model,
    grid: dict
):
    cv = model_selection.StratifiedKFold(4, shuffle=True, random_state=0)
    estimator = pipeline.Pipeline([
        ("select", RandomSelector),
        ("model", model)
    ])
    sizes = logstep(10, dataframe.shape[1], 0.5)
    seeds = range(1)
    grid = {
        "select__kw_args": [
            {"seed": seed, "size": size}for seed in seeds for size in sizes
        ],
        **{f"model__{key}": value for key, value in grid.items()}
    }
    search = model_selection.GridSearchCV(
        estimator,
        grid,
        scoring="f1_weighted",
        n_jobs=10,
        # verbose=1,
        cv=cv
    ).fit(dataframe, target).cv_results_
    return (
        pd.DataFrame(search)
        .drop(columns="params")
        .sort_values("rank_test_score", ignore_index=True)
    )

# %%
run_search(
    pangenome,
    target,
    ensemble.RandomForestClassifier(),
    {
        "n_estimators": [100, 200, 300],
        "criterion": ["gini", "entropy", "log_loss"],
        "max_features": ["sqrt", "log2", None],
        "bootstrap": [True, False],
        "random_state": [0]
    }
).to_csv(sys.stdout, index=False)


