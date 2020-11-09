"""Model : profiles, questions, possible answers and their weight."""
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, Dict

import pandas as pd
from pandas._typing import DataFrame


def load_qa(fn_csv: Path) -> DataFrame:
    """Load a CSV file containing the QA pairs.

    The CSV file is a view exported from Airtable with profiles,
    questions, possible answers and their weights.
    """
    # TODO rewrite, improve?
    df = pd.read_csv(fn_csv)
    # check column headers are those we expect
    expected_headers = set(
        ["Valeur de réponse", "Question", "Profil", "Pondération (1 à 4)"]
    )
    assert set(df.columns.to_list()) == expected_headers
    # drop orphan answers
    df.dropna(axis=0, how="any", inplace=True)
    # check that (profile, question, weight) are unique
    all_pqw = list(
        sorted(
            df[["Profil", "Question", "Pondération (1 à 4)"]].itertuples(index=False)
        )
    )
    assert all_pqw == list(sorted(set(all_pqw)))
    #
    return df


def df_to_nesteddict(
    df: pd.DataFrame,
) -> DefaultDict[str, DefaultDict[str, Dict[int, str]]]:
    """Convert a DataFrame to a nested dictionary.

    The nested dictionary is :
    Dict[Profile, Dict[Question, Dict[Weight, Answer]]]
    """
    # TODO Multi-Index to nested dictionary ?
    res: DefaultDict[str, DefaultDict[str, Dict[int, str]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    for p, qwa in df.groupby(by=["Profil"]):
        for q, wa in qwa.groupby(by=["Question"]):
            for w, a in wa[["Pondération (1 à 4)", "Valeur de réponse"]].itertuples(
                index=False
            ):
                res[p][q][w] = a
    return res


# TODO move back to app
CSV_QA = "data/qr_databat.csv"
df = load_qa(Path(CSV_QA))
print(df)
print(df_to_nesteddict(df))
