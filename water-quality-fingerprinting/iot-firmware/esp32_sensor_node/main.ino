/*
  ESP32 Water Quality Sensor Node -- Hybrid Real-Time Design

  Sends the 5 sensor-measurable parameters live via HTTP POST to the
  existing FastAPI /predict endpoint. BOD, fecal coliform, and total
  coliform are intentionally NOT sent -- the backend automatically falls
  back to this station's most recent lab-tested values for those three
  (see routes_predict.py's _fill_missing_lab_values()). This matches
  real-world water monitoring practice: continuous sensor readings
  combined with periodic lab confirmation for parameters that require
  bacterial culturing or multi-day incubation.

  Structure follows the same simple pattern as the original Wokwi
  prototype (potentiometers standing in for real sensors during
  simulation/testing) -- just sending via direct HTTP POST instead of
  MQTT, since the backend already speaks HTTP natively and needs no
  extra bridge service.

  Wokwi wiring (for simulation/testing before real sensors arrive):
    - Potentiometer 1 -> GPIO34  (stands in for pH probe)
    - Potentiometer 2 -> GPIO35  (stands in for conductivity probe)
    - Potentiometer 3 -> GPIO32  (stands in for dissolved oxygen sensor)
    - Potentiometer 4 -> GPIO33  (stands in for nitrate ISE sensor)
    - DS18B20 (or another potentiometer) -> temperature

  Real hardware wiring: replace each readX() function's analogRead() with
  the actual calibrated conversion formula for your specific sensor model.
*/

#include <WiFi.h>
#include <HTTPClient.h>

const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* BACKEND_URL = "http://YOUR_BACKEND_HOST:8000/predict";
const char* STATION_ID = "IOT_NODE_01";   // match this to a station_id already in your dashboard, or a new one
const int READING_YEAR = 2026;             // matches the "year" field the backend schema currently uses

void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
}

// ---- Sensor reads (Wokwi potentiometer stand-ins for now) ----
// Replace each with the real calibrated formula once actual sensors are wired in.

float readPH() {
  int raw = analogRead(34);
  return map(raw, 0, 4095, 0, 1400) / 100.0;   // maps to a 0.00-14.00 pH range
}

float readConductivity() {
  int raw = analogRead(35);
  return map(raw, 0, 4095, 0, 3000);            // maps to a 0-3000 umhos/cm range
}

float readDissolvedOxygen() {
  int raw = analogRead(32);
  return map(raw, 0, 4095, 0, 1200) / 100.0;    // maps to a 0.00-12.00 mg/L range
}

float readNitrate() {
  int raw = analogRead(33);
  return map(raw, 0, 4095, 0, 2000) / 100.0;    // maps to a 0.00-20.00 mg/L range
}

float readTemperature() {
  int raw = analogRead(25);
  return map(raw, 0, 4095, 150, 350) / 10.0;    // maps to a 15.0-35.0 C range
}

void sendReading() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected, skipping this reading");
    return;
  }

  float ph = readPH();
  float conductivity = readConductivity();
  float dissolvedOxygen = readDissolvedOxygen();
  float nitrate = readNitrate();
  float temperature = readTemperature();

  HTTPClient http;
  http.begin(BACKEND_URL);
  http.addHeader("Content-Type", "application/json");

  // Min = Max for a single instantaneous reading (matches the backend's
  // Min/Max schema, which was designed around the CPCB dataset structure).
  // Lab-only fields (bod, fecal_coliform, total_coliform) are deliberately
  // omitted -- the backend fills them from the last known lab test.
  String payload = String("{") +
    "\"station_id\":\"" + STATION_ID + "\"," +
    "\"year\":" + READING_YEAR + "," +
    "\"ph_min\":" + ph + ",\"ph_max\":" + ph + "," +
    "\"conductivity_min\":" + conductivity + ",\"conductivity_max\":" + conductivity + "," +
    "\"dissolved_oxygen_min\":" + dissolvedOxygen + ",\"dissolved_oxygen_max\":" + dissolvedOxygen + "," +
    "\"nitrate_min\":" + nitrate + ",\"nitrate_max\":" + nitrate + "," +
    "\"temperature_min\":" + temperature + ",\"temperature_max\":" + temperature +
  "}";

  Serial.println("Sending: " + payload);

  int responseCode = http.POST(payload);
  String response = http.getString();

  Serial.print("Response code: ");
  Serial.println(responseCode);
  Serial.println("Response body: " + response);

  http.end();
}

void setup() {
  Serial.begin(115200);
  connectWiFi();
}

void loop() {
  sendReading();
  delay(60000);  // send a reading every 60 seconds -- adjust as needed
}
