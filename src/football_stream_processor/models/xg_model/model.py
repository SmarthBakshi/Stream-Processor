from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier


def get_model(model_name: str = "logistic_regression"):
    if model_name == "logistic_regression":
      model = LogisticRegression(max_iter=1000)
      return model
    elif model_name == "xgboost":
      model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
      return model
    # else: What happens here?