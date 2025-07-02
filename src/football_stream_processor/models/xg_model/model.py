from sklearn.linear_model import LogisticRegression

def get_linear_model():
    # Logistic regression for binary classification (pass success/fail)
    model = LogisticRegression(max_iter=1000)
    return model