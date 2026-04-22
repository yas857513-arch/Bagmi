import asyncio
import socket
import os
import time
from fastapi import FastAPI

app = FastAPI()

# Data store karne ke liye
stats = {"sent": 0, "status": "idle", "target": None}

# Aapka Original Logic yahan hai
async def run_load_test(ip: str, port: int, players: int, duration: int):
    global stats
    stats["sent"] = 0
    stats["status"] = "running"
    stats["target"] = f"{ip}:{port}"
    
    # UDP Socket setup
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    end_time = time.time() + duration

    async def player_sim():
        while time.time() < end_time:
            try:
                # Aapka packet logic
                data = os.urandom(64)
                sock.sendto(data, (ip, port))
                stats["sent"] += 1
            except:
                pass
            # Aapka sleep timing
            await asyncio.sleep(0.05)

    # Players (Tasks) create karna
    tasks = [asyncio.create_task(player_sim()) for _ in range(players)]
    await asyncio.gather(*tasks)
    
    sock.close()
    stats["status"] = "finished"

# URL Endpoints
@app.get("/")
async def home():
    return {"message": "API is Live. Use /start?ip=... to begin."}

@app.get("/start")
async def start_test(ip: str, port: int, players: int = 10, duration: int = 30):
    # Background mein test shuru karega
    asyncio.create_task(run_load_test(ip, port, players, duration))
    return {
        "status": "Test Started",
        "details": {"ip": ip, "port": port, "players": players, "duration": duration}
    }

@app.get("/status")
async def get_status():
    return stats
    
