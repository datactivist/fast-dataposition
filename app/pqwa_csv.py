"""Model descriptions in a custom CSV format : PQWA CSV.

PQWA stands for Profiles, Questions, Weights and Answers.
The current implementation handles CSV files exported from Airtable, with their quirks.
"""
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, Dict, List

import pandas as pd


def load_pqwa(
    fn_csv: Path, pqwa_names: List[str], pedantic: bool = False
) -> pd.DataFrame:
    """Load a CSV file describing a PQWA model.

    Parameters
    ----------
    fn_csv
        Path to the CSV file.
    pqwa_names
        List of column names for respectively profile, question, weight, answer.
    pedantic
        If True, print the distribution of weights for debugging or introspection.
    """
    # unpack the column names
    assert len(pqwa_names) == 4
    col_p, col_q, col_w, col_a = pqwa_names
    # read the CSV file
    df = pd.read_csv(
        fn_csv,
        dtype={
            col_p: "string",
            col_q: "string",
            col_w: int,
            col_a: "string",
        },
    )
    # check that we read the expected column headers
    assert set(df.columns.to_list()) == set(pqwa_names)
    # rename columns
    df.rename(
        columns={
            col_p: "profile",
            col_q: "question",
            col_w: "weight",
            col_a: "answer",
        },
        inplace=True,
    )
    # FIXME strip leading and trailing '"' around "long text" fields in airtable
    # the CSV export from airtable has triple double quotes around "long text" fields,
    # single double quotes around "simple text" fields
    df["question"] = df["question"].str.strip('"')
    # drop incomplete lines, including orphan answers
    #  TODO add warning for dropped answers
    df.dropna(axis=0, how="any", inplace=True)
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
