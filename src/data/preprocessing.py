from typing import Tuple

import pandas as pd


def preprocess(
    data: pd.DataFrame, target_column: str
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Preprocessing the data for TRAINING step.

    param data: data to be preprocessed
    param target_column: name of the target column
    return: preprocessed data
    """

    data = data.set_index("id")
    minority_class = data[data[target_column] == 1]
    majority_class = data[data[target_column] == 0]

    majority_class_undersampled = majority_class.sample(
        n=len(minority_class), random_state=42
    )

    data = pd.concat([majority_class_undersampled, minority_class])
    return data.drop(target_column, axis=1), data[target_column]
