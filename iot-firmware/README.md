# IoT Firmware (Phase 2)

This folder holds the ESP32 sensor node firmware for Phase 2 of the project.

## Status
Placeholder — hardware not yet procured/deployed. `esp32_sensor_node/main.ino`
outlines the intended structure: read sensors → connect WiFi → POST JSON
reading to the FastAPI backend `/predict` endpoint.

## Phase 2 TODO
1. Procure sensors: pH, turbidity, TDS/conductivity, temperature (DS18B20),
   and investigate proxy/lab methods for BOD, COD, nitrate, fecal coliform
   (these usually can't be measured with cheap analog sensors directly).
2. Wire sensors to ESP32, calibrate against known standard solutions.
3. Fill in `readPH()`, `readTurbidity()`, `readTDS()`, `readTemperature()`
   with real ADC reads + calibration curves.
4. Update WiFi credentials and backend URL.
5. Implement a new ingestion source in
   `ml-pipeline/src/ingestion/` (e.g. `esp32_mqtt_source.py`) that
   implements `base_source.py`'s interface, OR post directly to
   `backend/app/api/routes_predict.py`.
6. Enable `backend/app/api/routes_stream.py` for real-time WebSocket
   push to the dashboard.
7. Validate end-to-end with real field data against known pollution
   sources for ground-truth accuracy testing.
