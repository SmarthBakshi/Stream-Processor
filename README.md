# Football Stream Processor

A modular Python project for extracting, processing, analyzing, and visualizing football (soccer) event data, with a focus on passes, carries, and shots. The project supports feature engineering, exploratory data analysis (EDA), and animation of match events using StatsBomb open data.

---

## Features

- **Data Pipeline:** Load, filter, and process StatsBomb event data for passes, carries, and shots.
- **Feature Engineering:** Add tactical, spatial, and contextual features for modeling (e.g., xG, pass success).
- **Exploratory Data Analysis (EDA):** Modular, reusable EDA utilities for missing values, class distribution, data types, duplicate removal, and visualizations.
- **Visualization:** Animated and static visualizations of passes, carries, and shots on a football pitch.
- **OOP Design:** Extensible, class-based utilities for EDA and feature engineering.
- **CLI Support:** Run scripts from the command line for data processing and visualization.

---

## Project Structure

```
football_stream_processor/
│
├── open-data/             # Downloaded StatsBomb open data
│
├── scripts/               # Scripts
│   └── eda.py             # EDA 
│
├── src/football_stream_processor/  # Source code for the project
│   ├── __init__.py
│   │
│   ├── animate/           # Contains animation visualizations script
│   │   ├── __init.py__
│   │   ├── animate_match.py    # Animates the entire match
│   │   └── animate_passes.py   # Animates match passes
│   │
│   ├── match/            # Contains match related scripts
│   │   ├── __init.py__
│   │   ├── match_summary.py    # Gives match summary
│   │   └── simualte.py    # Simulates match events in real time
│   │
│   ├── models/            # Machine learning models
│   │   ├── __init__.py
│   │   ├── xg_model/      # Pass prediction model
│   │   └── player_roles/  # Upcoming model
│   │
│   ├── utils/             # Utility functions and classes
│   │   ├── __init__.py
│   │   └── eda_utils.py  # EDA utility functions
│
│
├── .gitignore             # Git ignore file
├── .gitmodules            # Git modules file
├── README.md              # Project README
├── poetry.lock            # poetry lock file
├── pyproject.toml         # Contains dependencies
└── .python-version        # Contains python versions
```

---

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/SmarthBakshi/football_stream_processor.git
    cd football_stream_processor
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

```python
from football_stream_processor.utils.eda_utils import PassDataEDA
from football_stream_processor.models.xg_model.feat_engineering import add_engineered_features

df = pd.read_pickle(".pickle/pass_data.pkl")
df = add_engineered_features(df)
eda = PassDataEDA(df)
eda.missing_values()
eda.class_distribution()
eda.data_types()
df_clean = eda.remove_duplicates()
eda.eda_visualizations()  # Visualizations saved in resources/
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
---

## Customization

- **Add new features:** Extend `feat_engineering.py` with new feature functions.
- **Add new EDA steps:** Extend `eda_utils.py` or subclass `PassDataEDA`.
- **Visualizations:** Modify or add new plotting functions in the `animate/` directory.

---

## License

This project is licensed under the MIT License.

---

## Acknowledgements

- [StatsBomb Open Data](https://github.com/statsbomb/open-data)