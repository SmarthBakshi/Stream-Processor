from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

def get_model(model_name: str = "logistic_regression", **kwargs):
    if model_name == "logistic_regression":
      model = LogisticRegression(max_iter=1000)
      return model
    elif model_name == "xgboost":
      return XGBClassifier(
          n_estimators=kwargs.get("n_estimators", 100),
          learning_rate=kwargs.get("learning_rate", 0.1),
          max_depth=kwargs.get("max_depth", 6),
          subsample=kwargs.get("subsample", 1.0),
          colsample_bytree=kwargs.get("colsample_bytree", 1.0),
          eval_metric="logloss",
          use_label_encoder=False,
          random_state=42
      )
    raise ValueError(f"Unsupported model: {model_name}")