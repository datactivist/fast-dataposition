"""Model : profiles, questions, possible answers and their weight."""
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, Dict

import pandas as pd


def load_qa(fn_csv: Path, pedantic: bool = False) -> pd.DataFrame:
    """Load a CSV file containing the QA pairs.

    The CSV file is a view exported from Airtable with profiles,
    questions, possible answers and their weights.
    """
    # TODO rewrite, improve?
    df = pd.read_csv(
        fn_csv,
        dtype={
            "Valeur de réponse": "string",
            "Question": "string",
            "Profil": "string",
            "Pondération (1 à 4)": int,
        },
    )
    # check that the column headers are those we currently expect
    expected_headers = set(
        ["Valeur de réponse", "Question", "Profil", "Pondération (1 à 4)"]
    )
    assert set(df.columns.to_list()) == expected_headers
    # rename columns
    df.rename(
        columns={
            "Valeur de réponse": "answer",
            "Question": "question",
            "Profil": "profile",
            "Pondération (1 à 4)": "weight",
        },
        inplace=True,
    )
    # drop incomplete lines, including orphan answers
    #  TODO add warning for dropped answers
    df.dropna(axis=0, how="any", inplace=True)
    # display distribution of weights
    if pedantic:
        print("Distribution of weights:")
        print(df["weight"].value_counts().sort_index())
    # check that (profile, question, weight) are unique combinations:
    # the sorted list of values is equal to the sorted set of values
    all_pqw = list(
        sorted(df[["profile", "question", "weight"]].itertuples(index=False))
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
    # TODO use Multi-Index as intermediary structure to generate nested dictionary ?
    res: DefaultDict[str, DefaultDict[str, Dict[int, str]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    # keep the profiles, and the questions in each profile, ordered as in the CSV (sort=False)
    for p, qwa in df.groupby(by=["profile"], sort=False):
        for q, wa in qwa.groupby(by=["question"], sort=False):
            for w, a in sorted(wa[["weight", "answer"]].itertuples(index=False)):
                res[p][q][w] = a
    return res
