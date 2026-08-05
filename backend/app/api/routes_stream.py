"""
Phase 2 placeholder — WebSocket endpoint for live ESP32/IoT sensor data.

Not active in Phase 1. Once the IoT node is deployed, implement:
    - A WebSocket or MQTT-bridge endpoint here that receives live readings
    - Push each reading through the same InferenceService used by /predict
    - Broadcast predictions to connected dashboard clients in real time

Left as a stub now so the route module already exists and can be wired
into main.py without restructuring the API.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["stream"])


@router.websocket("/stream")
async def stream_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({
        "status": "not_implemented",
        "message": "Live IoT streaming will be enabled in Phase 2.",
    })
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
