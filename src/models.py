# %%
import functools as ft
import sys

import numpy as np
import pandas as pd
from sklearn import (
    ensemble,
    feature_selection,
    model_selection,
    pipeline,
    tree
)

# %% [markdown]
# ## Dataset loading

# %%
target = pd.read_csv(
    "accessions.tsv",
    sep="\t",
    index_col="genome"
)["fsp"]


# %%
data_files = [
    # "data/pangenome/pangenome.full.tsv",
    "data/pancluster/pancluster.raw.tsv",
    "data/pancluster/pancluster.grouped.tsv",
    "data/pancluster/pancluster.ordered.tsv",
]
dataframes = [
    pd.read_csv(file, sep="\t", index_col="genome") for file in data_files
]
dataframes

# %% [markdown]
# ## Grid definitions

# %%
def logstep(start: int, end: int, step: float):
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
cv = model_selection.StratifiedKFold(4, shuffle=True, random_state=0)
# %%
score_func = ft.partial(
    feature_selection.mutual_info_classif,
    discrete_features=True
)
# %%
tree_pipeline = pipeline.Pipeline([
    ("select", feature_selection.SelectKBest()),
    ("model", tree.DecisionTreeClassifier())
], memory="data/cache")
adaboost_pipeline = pipeline.Pipeline([
    ("select", feature_selection.SelectKBest()),
    ("model", ensemble.AdaBoostClassifier())
], memory="data/cache")
forest_pipeline = pipeline.Pipeline([
    ("select", feature_selection.SelectKBest()),
    ("model", ensemble.RandomForestClassifier())
], memory="data/cache")
pipelines = [tree_pipeline, adaboost_pipeline, forest_pipeline]

# %%
def create_search(
    dataframe: pd.DataFrame,
    target: pd.Series,
    pipeline: pipeline.Pipeline,
    grid: dict
):
    grid = {
        "select__score_func": [score_func],
        "select__k": logstep(10, dataframe.shape[1], 0.5),
        **{f"model__{key}": value for key, value in grid.items()}
    }
    print(dataframe, grid)
    return pd.DataFrame(model_selection.GridSearchCV(
        estimator=pipeline,
        param_grid=grid,
        scoring="f1_weighted",
        n_jobs=10,
        verbose=1
    ).fit(dataframe, target).cv_results_)

# %%
for df in [
    create_search(dataframe, target, estimator, grid)
    for estimator, grid in zip([pipelines[1]], [grids[1]])
    for dataframe in dataframes
]:
    df.to_csv(sys.stdout)
