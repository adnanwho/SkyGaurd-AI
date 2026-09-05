import pandas as pd

from src.skyguard.context.spatial import evaluate_spatial_context


def test_spatial_context_excludes_target_and_uses_nearest_neighbors():
    target = pd.Series({
        "station_id": "AWS-01",
        "latitude": 28.61,
        "longitude": 77.20,
        "temperature": 40.0,
    })
    neighbors = pd.DataFrame([
        {"station_id": "AWS-01", "latitude": 28.61, "longitude": 77.20, "temperature": 40.0},
        {"station_id": "AWS-02", "latitude": 28.62, "longitude": 77.21, "temperature": 30.0},
        {"station_id": "AWS-03", "latitude": 28.63, "longitude": 77.22, "temperature": 31.0},
    ])

    result = evaluate_spatial_context(target, neighbors)

    assert result["available"] is True
    assert result["neighbor_count"] == 2
    assert result["neighbor_station_ids"] == ["AWS-02", "AWS-03"]
    assert result["median"] == 30.5
    assert result["deviation"] == 9.5


def test_spatial_context_is_explicitly_unavailable_without_coordinates():
    target = pd.Series({"station_id": "AWS-01", "temperature": 30.0})
    result = evaluate_spatial_context(target, pd.DataFrame([{"station_id": "AWS-02", "temperature": 31.0}]))

    assert result["available"] is False
