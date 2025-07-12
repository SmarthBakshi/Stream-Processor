import pickle


# "Util" as module is an anti-pattern. Give it a specific name "pickle_helpers.py" maybe
def save_model(model, filepath: str):
    with open(filepath, "wb") as f:
        pickle.dump(model, f)

def load_model(filepath: str):
    with open(filepath, "rb") as f:
        return pickle.load(f)