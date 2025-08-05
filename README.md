# Football Stream Processor

A modular Python project for extracting, processing, analyzing, and visualizing football (soccer) event data, with a focus on passes, carries, and shots. The project features advanced machine learning models for predicting pass success, alongside robust support for feature engineering, exploratory data analysis (EDA), and animated visualizations of match events using StatsBomb open data.

---
---

## 🎥 Demo

<video width="100%" controls>
  <source src="media/demo.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

---

## Features

- **Data Pipeline:** Load, filter, and process StatsBomb event data for passes, carries, and shots.  
- **Feature Engineering:** Add tactical, spatial, and contextual features for modeling (e.g., xG, pass success).  
- **Machine Learning Model:** Advanced models for predicting pass success, tracked via MLflow.  
- **Exploratory Data Analysis (EDA):** Utilities for missing values, class distribution, data types, duplicate removal, and visualizations.  
- **Visualization:** Animated and static visualizations of passes, carries, and shots on a football pitch.  
- **Web App:** Interactive Streamlit dashboard for match insights, pass networks, shot maps, and model leaderboards.  

---

## Project Structure

```
football_stream_processor/
├── .github/               # Contains CI workflows
├── open-data/             # Git submodule: StatsBomb open data
│   └── data/
|       └── events/        # Contains events json files    
|       └── matches/       # Contains matches json files    
├── scripts/               # Standalone scripts
│   └── eda.py             # Run EDA from the command line
│
├── resources/             # Contains visualizations, figures, and generated assets
│
├── src/                   # Source code for the project
|   ├── app/               # Streamlit application
|   │ │ ├── components/    # Reusable UI components
|   │ │ ├── webpages/      # Page modules (overview, analysis, insights)
|   │ │ └── main.py        # Entry-point for Streamlit
│   └── __init__.py
│   
|   ├── football_stream_processor   # Core library
│   │   ├── animation/              # Contains animation visualizations script
│   │   │   ├── __init.py__
│   │   │   ├── animate_match.py    # Animates the entire match
│   │   │   └── animate_passes.py   # Animates match passes
│   │   │
│   │   ├── match/                  # Contains match related scripts
│   │   │   ├── __init.py__
│   │   │   ├── match_summary.py    # Gives match summary
│   │   │   └── simualte.py         # Simulates match events in real time
│   │   │
│   │   ├── models/                 # Machine learning models
│   │   │   ├── __init__.py  
│   │   │   ├── xg_model/           # Pass prediction model
│   │   │
│   └── └── utils/                  # Utility functions and classes
│           ├── __init__.py
│           ├── animation_utils.py 
│           └── eda_utils.py        #  EDA utility functions
│
├── tests/                 # Unit and integration tests
├── Dockerfile             # Multi-stage Docker build for the web app
├── .dockerignore          # Docker ignore file
├── .gitignore             # Git ignore file
├── .gitmodules            # Git modules file
├── README.md              # Project README
├── poetry.lock            # poetry lock file
├── pyproject.toml         # Contains dependencies
├── .python-version        # Contains python versions
└── LICENCE
```

---

## Installation

1. **Clone the repo and submodule:**

   ```bash
   git clone https://github.com/SmarthBakshi/Stream-Processor.git
   cd Stream-Processor
   git submodule update --init --recursive
   ```

2. **Install Poetry (if not already installed)**

    ```sh
    curl -sSL https://install.python-poetry.org | python3 -
    ```

3. **Install dependencies:**

    ```sh
    poetry install 
    ```

---

## Usage

### Data Preparation

To prepare the pass data dataframe, run:

```bash
poetry run python data_pipeline.py --limit 100
```

The `--limit` argument specifies the number of event JSON files to use for preparing the `pass_data` dataframe.

### Exploratory Data Analysis (EDA) & Feature Engineering

```bash
poetry run python scripts/eda.py
```

### Animation

```bash
python animate/animate_passes.py --file open-data/data/events/22912.json --save
python animate/animate_match.py --file open-data/data/events/22912.json --save
```

### Model Training & Evaluation

To train the xG prediction model, run:

```bash
python src/football_stream_processor/models/xg_model/train.py
```

### Launch Web Dashboard

```bash
poetry run streamlit run src/app/main.py \
  --server.port=8501 --server.enableCORS=false
```

---

## Docker

#### Build and run the Streamlit dashboard using Docker

- Run the `train.py` script to have the mlflow runs and experiments stored in `mlflow/`
- Build the Docker Image

```bash
docker build -t football-dashboard .
```

- Run the docker Image

```bash
 docker run --rm \              
  -p 8501:8501 \
  -v $(pwd)/open-data:/app/open-data \
  -v $(pwd)/mlflow/mlruns:/app/mlflow/mlruns football-dashboard
```

## CI/CD

- **GitHub Actions** (.github/workflows/ci.yml):
    1. Checks out code
    2. Installs Poetry & dependencies
    3. Runs pytest & linting (ruff)

## Deployment

You can deploy the Docker image to any container host (Render, AWS ECS/Fargate, etc.).
Be sure to mount or include the open-data/data folder and set environment variables:
***MLFLOW_TRACKING_URI*** & ***MLFLOW_EXPERIMENT_NAME***

## Customization

- **Add new features:** Extend `feat_engineering.py` with new feature functions.
- **Add new EDA steps:** Extend `eda_utils.py` or subclass `PassDataEDA`.
- **Visualizations:** Modify or add new plotting functions in the `animate/` directory.
- **Log MLFlow results:** Change the 'MLFLOW_TRACKING_URI' in config.py to log locally or to a remote server

---

## License

This project is licensed under the MIT License.

---

## Acknowledgements

- [StatsBomb Open Data](https://github.com/statsbomb/open-data)
- [Streamlit](https://streamlit.io/)
- [MLflow](https://mlflow.org/)
- [mplsoccer](https://mplsoccer.readthedocs.io/en/latest/)
- [Optuna](https://optuna.org/)
