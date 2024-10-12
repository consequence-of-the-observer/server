from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import uuid
import json
import sqlite3

class Dice(BaseModel):
    diceCount: int
    d4: int
    d6: int
    d8: int
    d10: int
    d100: int
    d12: int
    d20: int
    reason: str


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []


    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(self.active_connections)


    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)


    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


playerManager = ConnectionManager()
gameMasterManager = ConnectionManager()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
async def get():
    return {"hello":"world"}

@app.websocket("/player")
async def websocket_endpoint(websocket: WebSocket):
    await playerManager.connect(websocket)
    print(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print("data received")
            await playerManager.send_personal_message(data, websocket)
            await gameMasterManager.broadcast(data)
    except WebSocketDisconnect:
        playerManager.disconnect(websocket)
        await playerManager.broadcast(f"left the chat")


@app.websocket("/gameMaster")
async def websocket_endpoint(websocket: WebSocket):
    await gameMasterManager.connect(websocket)
    print(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print("data received")
            await gameMasterManager.send_personal_message(data, websocket)
    except WebSocketDisconnect:
        gameMasterManager.disconnect(websocket)
        await gameMasterManager.broadcast(f"left the chat")
