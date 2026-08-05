/*
  Phase 2 placeholder — ESP32 water quality sensor node.

  Intended sensors (adjust to what you actually procure):
    - pH sensor
    - Turbidity sensor
    - TDS/Conductivity sensor
    - DS18B20 temperature sensor
    - (Optional) DO sensor

  Intended flow:
    1. Read raw analog/digital values from each sensor
    2. Convert to calibrated engineering units matching backend schema:
       ph, dissolved_oxygen, bod, cod, turbidity, tds, conductivity,
       nitrate, fecal_coliform, temperature
       (BOD/COD/nitrate/fecal_coliform typically need lab calibration or
       proxy sensors — plan this during Phase 2 hardware selection)
    3. Connect to WiFi
    4. POST JSON reading to backend /predict endpoint (or a dedicated
       ingestion endpoint), OR publish to an MQTT broker that a bridge
       service forwards into the FastAPI backend

  This file is a structural placeholder — fill in actual sensor pin
  wiring and calibration once hardware is procured.
*/

#include <WiFi.h>
#include <HTTPClient.h>

const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* BACKEND_URL = "http://YOUR_BACKEND_HOST:8000/predict";
const char* STATION_ID = "IOT_NODE_01";

void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
}

// Placeholder — replace with actual sensor reads
float readPH() { return 7.0; }
float readTurbidity() { return 5.0; }
float readTDS() { return 300.0; }
float readTemperature() { return 25.0; }

void sendReading() {
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  http.begin(BACKEND_URL);
  http.addHeader("Content-Type", "application/json");

  String payload = String("{") +
    "\"station_id\":\"" + STATION_ID + "\"," +
    "\"ph\":" + readPH() + "," +
    "\"dissolved_oxygen\":5.0," +
    "\"bod\":3.0," +
    "\"cod\":10.0," +
    "\"turbidity\":" + readTurbidity() + "," +
    "\"tds\":" + readTDS() + "," +
    "\"conductivity\":500.0," +
    "\"nitrate\":2.0," +
    "\"fecal_coliform\":100.0," +
    "\"temperature\":" + readTemperature() +
  "}";

  int responseCode = http.POST(payload);
  Serial.print("Response code: ");
  Serial.println(responseCode);
  http.end();
}

void setup() {
  Serial.begin(115200);
  connectWiFi();
}

void loop() {
  sendReading();
  delay(60000); // send a reading every 60 seconds
}
