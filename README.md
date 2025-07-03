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
├── data/                  # Raw and processed data
│   ├── open-data/         # Downloaded StatsBomb open data
│   └── processed/         # Processed data ready for analysis
│
├── docs/                  # Documentation files
│
├── football_stream_processor/  # Source code for the project
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   ├── models/            # Machine learning models
│   │   ├── __init__.py
│   │   ├── xg_model/      # Expected goals model
│   │   └── ...
│   │
│   ├── utils/             # Utility functions and classes
│   │   ├── __init__.py
│   │   ├── data_utils.py  # Data loading and processing utilities
│   │   ├── viz_utils.py   # Visualization utilities
│   │   └── ...
│   │
│   └── ...
│
├── tests/                 # Unit and integration tests
│
├── .gitignore             # Git ignore file
├── README.md              # Project README
└── requirements.txt       # Python package dependencies
```

---

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/football_stream_processor.git
    cd football_stream_processor
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```
    Or use [Poetry](https://python-poetry.org/) if preferred.

3. **Download StatsBomb open data:**
    - Place event JSON files in [events](http://_vscodecontentref_/1).

---

## Usage

### Data Pipeline & Feature Engineering

```python
from football_stream_processor.models.xg_model.data_pipeline import build_pass_dataset
from football_stream_processor.models.xg_model.feat_engineering import add_engineered_features

df = build_pass_dataset("open-data/data/events/22912.json")
df = add_engineered_features(df)
```

### Exploratory Data Analysis (EDA)

```python
from football_stream_processor.utils.eda_utils import PassDataEDA

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
python animate/animate_carries_shots.py --file open-data/data/events/22912.json --save
```

---

## Customization

- **Add new features:** Extend `feat_engineering.py` with new feature functions.
- **Add new EDA steps:** Extend `eda_utils.py` or subclass `PassDataEDA`.
- **Visualizations:** Modify or add new plotting functions in the `animate/` directory.

---

## Contributing

Pull requests and issues are welcome! Please lint and test your code before submitting.

---

## License

This project is licensed under the MIT License.

---

## Acknowledgements

- [StatsBomb Open Data](https://github.com/statsbomb/open-data)
- [matplotlib](https://matplotlib.org/)