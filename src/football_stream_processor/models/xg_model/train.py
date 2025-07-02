import os
from sklearn.metrics import accuracy_score

from .data_preparation import load_and_prepare_data
from .model import get_linear_model
from .evaluation import print_classification_report, print_roc_auc, plot_confusion_matrix
from .utils import save_model

def main():
    # data_path = os.path.expanduser("~/data/pass_data.csv")  # Change path accordingly
    model_save_path = os.path.expanduser("~/models/.pickle/linear_model.pkl")
    
    X_train, X_test, y_train, y_test = load_and_prepare_data()
    
    model = get_linear_model()
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    y_probs = model.predict_proba(X_test)[:, 1]
    
    print_classification_report(y_test, y_pred)
    print_roc_auc(y_test, y_probs)
    plot_confusion_matrix(y_test, y_pred)
    
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    save_model(model, model_save_path)
    print(f"Model saved to {model_save_path}")

if __name__ == "__main__":
    main()