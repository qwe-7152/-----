import csv
from datetime import datetime, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).parent
INPUT_PATH = BASE_DIR / "asos_108_2023_2024.csv"
OUTPUT_PATH = BASE_DIR / "wind_dataset.csv"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def read_observations() -> dict[datetime, dict[str, str]]:
    observations: dict[datetime, dict[str, str]] = {}
    with INPUT_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            observation_time = datetime.strptime(row["datetime"], TIME_FORMAT)
            observations[observation_time] = row
    return observations


def build_hourly_rows(
    observations: dict[datetime, dict[str, str]],
) -> list[dict[str, str]]:
    first_time = min(observations)
    last_time = max(observations)
    hourly: dict[datetime, dict[str, str]] = {}
    current_time = first_time
    while current_time <= last_time:
        hourly[current_time] = observations.get(current_time, {})
        current_time += timedelta(hours=1)

    rows: list[dict[str, str]] = []
    for prediction_time in hourly:
        target_time = prediction_time + timedelta(hours=1)
        previous_one = prediction_time - timedelta(hours=1)
        previous_two = prediction_time - timedelta(hours=2)
        current = hourly[prediction_time]
        target = hourly.get(target_time, {})
        one_hour_ago = hourly.get(previous_one, {})
        two_hours_ago = hourly.get(previous_two, {})

        values = (
            current.get("wind_speed_ms", ""),
            current.get("temperature_C", ""),
            current.get("humidity_pct", ""),
            one_hour_ago.get("wind_speed_ms", ""),
            two_hours_ago.get("wind_speed_ms", ""),
            target.get("wind_speed_ms", ""),
        )
        if any(value == "" for value in values):
            continue

        rows.append(
            {
                "prediction_time": prediction_time.strftime(TIME_FORMAT),
                "target_time": target_time.strftime(TIME_FORMAT),
                "wind_speed_ms": current["wind_speed_ms"],
                "temperature_C": current["temperature_C"],
                "humidity_pct": current["humidity_pct"],
                "wind_speed_1h_ago_ms": one_hour_ago["wind_speed_ms"],
                "wind_speed_2h_ago_ms": two_hours_ago["wind_speed_ms"],
                "target_wind_speed_ms": target["wind_speed_ms"],
            }
        )
    return rows


def main() -> None:
    observations = read_observations()
    rows = build_hourly_rows(observations)
    fieldnames = [
        "prediction_time",
        "target_time",
        "wind_speed_ms",
        "temperature_C",
        "humidity_pct",
        "wind_speed_1h_ago_ms",
        "wind_speed_2h_ago_ms",
        "target_wind_speed_ms",
    ]
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"hourly_rows={((max(observations) - min(observations)).total_seconds() // 3600) + 1:.0f}")
    print(f"saved_rows={len(rows)}")


if __name__ == "__main__":
    main()
