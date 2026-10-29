# ⚙️ Backend Layer

The backend layer is a modular Python API gateway and machine learning analysis service.

## Architecture

```
backend/
├── models/
│   └── moringa_model.pkl        # Trained Random Forest classifier
├── src/
│   ├── app.py                  # Server factory & static file resolver
│   ├── config/
│   │   └── settings.py         # Environment configuration
│   ├── controllers/
│   │   └── sensor_controller.py# HTTP request handlers & state
│   ├── middleware/
│   │   └── cors.py             # CORS & OPTIONS preflight
│   ├── routes/
│   │   └── api_routes.py       # API route dispatcher
│   ├── services/
│   │   ├── analysis_service.py # Spectral math (Red-edge, NIR, LPQI)
│   │   ├── ml_service.py       # Feature scaling & model inference
│   │   └── sensor_service.py   # SensorClient HTTP driver
│   ├── utils/
│   │   └── response.py         # JSON and file response formatting
│   └── validators/
│       └── sensor_validator.py # Payload format and band checks
├── server.py                   # CLI Server runner
├── requirements.txt            # Backend dependencies
└── README.md
```

## Running the Backend

From the project root:
```bash
python3 backend/server.py
```

With custom options:
```bash
python3 backend/server.py --port 5050 --sensor-url http://10.149.144.149/scan
```
