from sklearn.metrics import (
    classification_report,
    ConfusionMatrixDisplay, 
    roc_auc_score
)

import matplotlib.pyplot as plt


def print_classification_report(y_true, y_pred):
    print(classification_report(y_true, y_pred))

def print_roc_auc(y_true, y_probs):
    auc = roc_auc_score(y_true, y_probs)
    print(f"ROC AUC Score: {auc:.4f}")

def plot_confusion_matrix(y_true, y_pred, save_path=None):
    cm_display = ConfusionMatrixDisplay.from_predictions(y_true, y_pred)
    plt.title("Confusion Matrix")

    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
    plt.close()