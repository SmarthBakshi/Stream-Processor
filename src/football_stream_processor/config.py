# Model training
MODEL_NAME = "xgboost"
RANDOM_SEED = 42
TEST_SIZE = 0.2

# Paths
MODEL_DIR = "models"
MODEL_FILENAME_TEMPLATE = "{model_name}_model.pkl"
MODEL_SAVE_PATH = MODEL_DIR + "/" + MODEL_FILENAME_TEMPLATE.format(model_name=MODEL_NAME)
PLOT_DIR = "resources/plots"
PICKLE_DIR = ".pickle"
RESOURCES_DIR = "resources"