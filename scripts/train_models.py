import pandas as pd

from src.skyguard.detection.baseline import train_baseline


if __name__ == "__main__":
    data = pd.read_csv("data/processed/SkyGuard_clean_3hourly.csv")
    print(train_baseline(data))
