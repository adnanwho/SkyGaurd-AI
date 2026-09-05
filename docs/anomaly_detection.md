# Anomaly Detection

The current ensemble uses Isolation Forest, ECOD, COPOD, and HBOS over engineered weather features. The implementation and thresholds remain in `src/skyguard/detection/ensemble.py` and `src/skyguard/config.py`.

The optional persisted clean baseline is handled by `src/skyguard/detection/baseline.py`. SHAP attribution is optional and reports feature contribution, not causal proof. LSTM autoencoder support remains optional until TensorFlow is installed.
