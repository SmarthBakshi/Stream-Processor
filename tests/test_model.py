import pytest
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from football_stream_processor.models.xg_model.model import get_model

def test_get_model_logistic_regression():
    model = get_model("logistic_regression")
    assert isinstance(model, LogisticRegression)
    assert model.max_iter == 1000

def test_get_model_xgboost_default_params():
    model = get_model("xgboost")
    assert isinstance(model, XGBClassifier)
    assert model.n_estimators == 100
    assert model.learning_rate == 0.1
    assert model.max_depth == 6
    assert model.subsample == 1.0
    assert model.colsample_bytree == 1.0
    assert model.eval_metric == "logloss"

def test_get_model_xgboost_custom_params():
    model = get_model("xgboost", n_estimators=200, learning_rate=0.2, max_depth=10)
    assert model.n_estimators == 200
    assert model.learning_rate == 0.2
    assert model.max_depth == 10

def test_get_model_invalid_name():
    with pytest.raises(ValueError) as excinfo:
        get_model("invalid_model")
    assert "Unsupported model" in str(excinfo.value)
