# %%
import numpy as np
import pandas as pd
from sklearn import (
    ensemble,
    feature_selection,
    model_selection,
    pipeline,
)

# %%
target = pd.read_csv("accessions.tsv", sep="\t", index_col="genome")["fsp"]
files = [
    "data/pangenome/pangenome.full.tsv",
    "data/pancluster/pancluster.raw.tsv",
    "data/pancluster/pancluster.grouped.tsv",
    "data/pancluster/pancluster.ordered.tsv",
]
dataframes = [pd.read_csv(file, sep="\t", index_col="genome") for file in files]

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
def run_search(
    dataframe: pd.DataFrame,
    target: pd.Series,
    model,
    grid: dict
):
    cv = model_selection.StratifiedKFold(4, shuffle=True, random_state=0)
    mi = feature_selection.mutual_info_classif(
        dataframe, target, discrete_features=True
    )
    estimator = pipeline.Pipeline([
        ("select", feature_selection.SelectKBest(lambda x, y: mi)),
        ("model", model)
    ])
    grid = {
        "select__k": logstep(10, dataframe.shape[1], 0.5),
        **{f"model__{key}": value for key, value in grid.items()}
    }
    search = model_selection.GridSearchCV(
        estimator,
        grid,
        scoring="f1_weighted",
        n_jobs=10,
        verbose=1,
        cv=cv
    ).fit(dataframe, target).cv_results_
    return (
        pd.DataFrame(search)
        .drop(columns="params")
        .sort_values("rank_test_score", ignore_index=True)
    )

# %%
for i, dataframe in enumerate(dataframes):
    run_search(
        dataframe,
        target,
        ensemble.RandomForestClassifier(),
        {
            "n_estimators": [100, 200, 300],
            "criterion": ["gini", "entropy", "log_loss"],
            "max_features": ["sqrt", "log2", None],
            "bootstrap": [True, False],
            "random_state": [0],
            "ccp_alpha": np.linspace(0, 0.2, 6)
        }
    ).to_csv(f"results_{i}.csv", index=False)


