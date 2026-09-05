from src.skyguard.ingestion.csv_loader import simulate_observations


if __name__ == "__main__":
    simulate_observations().to_csv("data/evaluation/simulated_observations.csv", index=False)
    print("Wrote data/evaluation/simulated_observations.csv")
