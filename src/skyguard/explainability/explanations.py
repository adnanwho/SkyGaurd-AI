from __future__ import annotations

from typing import Any

import pandas as pd


def explain_observation(row: pd.Series, model: Any = None, feature_values: pd.Series | None = None) -> dict[str, Any]:
    """Return feature attribution when SHAP is installed, otherwise an honest fallback."""
    if model is not None and feature_values is not None:
        try:
            import shap

            values = feature_values.to_frame().T
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(values)
            if isinstance(shap_values, list):
                shap_values = shap_values[-1]
            contributions = {
                name: float(value)
                for name, value in zip(values.columns, shap_values[0])
            }
            return {
                "available": True,
                "method": "SHAP TreeExplainer",
                "feature_contributions": contributions,
                "note": "Feature contribution only; not causal proof.",
            }
        except (ImportError, AttributeError, TypeError, ValueError, RuntimeError):
            pass
    return {
        "available": False,
        "method": "evidence fallback",
        "feature_contributions": {},
        "note": "SHAP is unavailable; explanation uses QC, temporal, spatial, and model evidence.",
    }


def explain_batch(model: Any, values: pd.DataFrame) -> pd.DataFrame:
    """Add safe row-level top SHAP attribution for a fitted tree model."""
    output = pd.DataFrame(index=values.index)
    output["SHAP_Available"] = False
    output["SHAP_Top_Feature"] = "Unavailable"
    output["SHAP_Top_Contribution"] = 0.0
    output["SHAP_Note"] = "SHAP attribution unavailable; this is not causal evidence."
    try:
        import shap

        shap_values = shap.TreeExplainer(model).shap_values(values)
        if isinstance(shap_values, list):
            shap_values = shap_values[-1]
        contributions = pd.DataFrame(shap_values, index=values.index, columns=values.columns)
        top_features = contributions.abs().idxmax(axis=1)
        output["SHAP_Available"] = True
        output["SHAP_Top_Feature"] = top_features
        output["SHAP_Top_Contribution"] = [
            float(contributions.loc[index, feature])
            for index, feature in top_features.items()
        ]
        output["SHAP_Note"] = "Feature contribution only; not causal proof."
    except (ImportError, AttributeError, TypeError, ValueError, RuntimeError):
        pass
    return output
