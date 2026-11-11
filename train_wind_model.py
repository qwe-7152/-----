import csv
from datetime import datetime
from pathlib import Path

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.ensemble import RandomForestRegressor


BASE_DIR = Path(__file__).parent
INPUT_PATH = BASE_DIR / "wind_dataset.csv"
OUTPUT_PATH = BASE_DIR / "predictions.csv"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
FEATURE_COLUMNS = [
    "wind_speed_ms",
    "wind_speed_1h_ago_ms",
    "wind_speed_2h_ago_ms",
    "temperature_C",
    "humidity_pct",
]


def load_rows() -> list[dict[str, str]]:
    with INPUT_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    return sorted(rows, key=lambda row: datetime.strptime(row["target_time"], TIME_FORMAT))


def to_features(row: dict[str, str]) -> list[float]:
    return [float(row[column]) for column in FEATURE_COLUMNS]


def main() -> None:
    rows = load_rows()
    train_rows = [
        row
        for row in rows
        if "2023-01-01 00:00:00" <= row["target_time"] <= "2024-11-30 23:00:00"
    ]
    evaluation_rows = [
        row
        for row in rows
        if "2024-12-01 00:00:00" <= row["target_time"] <= "2024-12-31 23:00:00"
    ]

    model = LinearRegression()
    model.fit(
        [to_features(row) for row in train_rows],
        [float(row["target_wind_speed_ms"]) for row in train_rows],
    )
    random_forest = RandomForestRegressor(
        n_estimators=100,
        max_depth=6,
        min_samples_leaf=5,
        random_state=42,
    )
    random_forest.fit(
        [to_features(row) for row in train_rows],
        [float(row["target_wind_speed_ms"]) for row in train_rows],
    )

    predictions: list[dict[str, str]] = []
    actual_values: list[float] = []
    persistence_values: list[float] = []
    regression_values: list[float] = []
    random_forest_values: list[float] = []
    for row in evaluation_rows:
        actual = float(row["target_wind_speed_ms"])
        persistence = float(row["wind_speed_ms"])
        regression = max(0.0, float(model.predict([to_features(row)])[0]))
        forest = max(0.0, float(random_forest.predict([to_features(row)])[0]))
        actual_values.append(actual)
        persistence_values.append(persistence)
        regression_values.append(regression)
        random_forest_values.append(forest)
        predictions.append(
            {
                "prediction_time": row["prediction_time"],
                "target_time": row["target_time"],
                "actual_wind_speed_ms": row["target_wind_speed_ms"],
                "current_wind_speed_prediction_ms": row["wind_speed_ms"],
                "linear_regression_prediction_ms": f"{regression:.10g}",
                "random_forest_prediction_ms": f"{forest:.10g}",
            }
        )

    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as file:
        fieldnames = list(predictions[0])
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(predictions)

    print(f"training_rows={len(train_rows)}")
    print(f"evaluation_rows={len(evaluation_rows)}")
    baseline_mae = mean_absolute_error(actual_values, persistence_values)
    regression_mae = mean_absolute_error(actual_values, regression_values)
    forest_mae = mean_absolute_error(actual_values, random_forest_values)
    print(f"current_wind_mae={baseline_mae:.10f}")
    print(f"linear_regression_mae={regression_mae:.10f}")
    print(f"random_forest_mae={forest_mae:.10f}")
    print(f"linear_regression_minus_baseline={regression_mae - baseline_mae:.10f}")
    print(f"random_forest_minus_baseline={forest_mae - baseline_mae:.10f}")
    print(f"random_forest_minus_linear_regression={forest_mae - regression_mae:.10f}")
    print("first_evaluation=")
    print(predictions[0])


if __name__ == "__main__":
    main()
