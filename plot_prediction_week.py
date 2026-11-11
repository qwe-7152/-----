import csv
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error


BASE_DIR = Path(__file__).parent
INPUT_PATH = BASE_DIR / "predictions.csv"
OUTPUT_PATH = BASE_DIR / "prediction_week.png"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def main() -> None:
    with INPUT_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    for row in rows:
        row["target_datetime"] = datetime.strptime(row["target_time"], TIME_FORMAT)

    december_rows = [
        row
        for row in rows
        if datetime(2024, 12, 1) <= row["target_datetime"] <= datetime(2024, 12, 31, 23)
    ]
    week_rows = [
        row
        for row in december_rows
        if datetime(2024, 12, 1) <= row["target_datetime"] <= datetime(2024, 12, 7, 23)
    ]

    times = [row["target_datetime"] for row in week_rows]
    actual = [float(row["actual_wind_speed_ms"]) for row in week_rows]
    baseline = [float(row["current_wind_speed_prediction_ms"]) for row in week_rows]
    regression = [float(row["linear_regression_prediction_ms"]) for row in week_rows]

    plt.figure(figsize=(14, 6))
    plt.plot(times, actual, color="black", label="Actual")
    plt.plot(times, baseline, color="gray", linestyle="--", label="Baseline (current wind)")
    plt.plot(times, regression, color="blue", label="Linear regression")
    plt.xlabel("Target time (KST)")
    plt.ylabel("Wind speed (m/s)")
    plt.title("Wind-speed predictions: 2024-12-01 to 2024-12-07 (KST)")
    plt.legend()
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=150)
    plt.close()

    print(f"plotted_rows={len(week_rows)}")
    print(f"december_rows={len(december_rows)}")
    print(
        "december_baseline_mae="
        f"{mean_absolute_error([float(row['actual_wind_speed_ms']) for row in december_rows], [float(row['current_wind_speed_prediction_ms']) for row in december_rows]):.10f}"
    )
    print(
        "december_linear_regression_mae="
        f"{mean_absolute_error([float(row['actual_wind_speed_ms']) for row in december_rows], [float(row['linear_regression_prediction_ms']) for row in december_rows]):.10f}"
    )


if __name__ == "__main__":
    main()
