# 풍속 예측

ASOS 108 관측자료를 이용해 1시간 뒤 풍속을 예측하는 프로젝트입니다. 모든 시각은 KST 기준입니다.

## 파일

- `asos_108_2023_2024.csv`: 원본 관측자료
- `make_wind_dataset.py`: 누락 시각을 보강하고 학습용 데이터셋 생성
- `wind_dataset.csv`: 시간별 입력·정답 데이터셋
- `train_wind_model.py`: 선형회귀와 랜덤포레스트 학습 및 평가
- `predictions.csv`: 2024년 12월 평가 결과
- `plot_prediction_week.py`: 2024년 12월 1~7일 예측 그래프 생성
- `prediction_week.png`: 주간 예측 그래프

## 입력과 정답

각 예측 행은 다음 5개 입력을 사용합니다.

1. 현재 풍속
2. 1시간 전 풍속
3. 2시간 전 풍속
4. 현재 기온
5. 현재 습도

정답은 정확히 1시간 뒤의 실제 풍속입니다. 입력 또는 정답에 필요한 값이 비어 있는 행은 저장하지 않습니다.

## 실행

```powershell
python make_wind_dataset.py
python train_wind_model.py
python plot_prediction_week.py
```

현재 Python 환경에서 실행할 때는 다음과 같이 실행할 수 있습니다.

```powershell
& 'C:/Users/User/AppData/Local/Programs/Python/Python314/python.exe' make_wind_dataset.py
& 'C:/Users/User/AppData/Local/Programs/Python/Python314/python.exe' train_wind_model.py
& 'C:/Users/User/AppData/Local/Programs/Python/Python314/python.exe' plot_prediction_week.py
```

필요한 주요 패키지는 `scikit-learn`과 `matplotlib`입니다.

## 학습·평가 기간

- 학습: 정답시각 2023-01-01 ~ 2024-11-30
- 평가: 정답시각 2024-12-01 00:00 ~ 2024-12-31 23:00
- 데이터는 시간순으로 정렬하며, 평가 중에는 재학습하지 않습니다.
- 음수 예측값은 0으로 치환합니다.

랜덤포레스트 설정은 다음과 같습니다.

- 트리 수: 100
- 최대 깊이: 6
- 끝가지 최소 표본 수: 5
- 무작위 시드: 42

## 최근 실행 결과

평가 행수는 744행이며, 12월 전체 MAE는 다음과 같습니다.

| 방법 | MAE (m/s) |
|---|---:|
| 현재 풍속 유지 | 0.6534946237 |
| 선형회귀 | 0.5945766854 |
| 랜덤포레스트 | 0.5938072290 |

`prediction_week.png`는 2024-12-01 00:00부터 2024-12-07 23:00까지를 표시하며, 실제값·기준 예측·선형회귀 예측·랜덤포레스트 예측을 비교할 수 있습니다.
