import pandas as pd
from src.models.model_definitions import Model

def infer(model: Model, data: pd.DataFrame) -> pd.DataFrame:
  data = data.set_index('id')
  predictions = model.predict(data)

  return pd.DataFrame(predictions, index=data.index, columns=['predictions'])