import asyncio
import socket
import os
import time
from fastapi import FastAPI

app = FastAPI()

# Global counter for results
stats = {"sent": 0, "status": "idle"}

async def run_load_test(ip: str, port: int, players: int, duration: int):
    global stats
    stats["sent"] = 0
    stats["status"] = "running"
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    end_time = time.time() + duration

    async def player_sim():
        while time.time() < end_time:
            try:
                data = os.urandom(64)
                sock.sendto(data, (ip, port))
                stats["sent"] += 1
            except:
                pass
            await asyncio.sleep(0.05)

    tasks = [asyncio.create_task(player_sim()) for _ in range(players)]
    await asyncio.gather(*tasks)
    
    sock.close()
    stats["status"] = "finished"

@app.get("/start")
async def start_test(ip: str, port: int, players: int = 10, duration: int = 30):
    # Background task chalayenge taaki URL immediately respond kare
    asyncio.create_task(run_load_test(ip, port, players, duration))
    return {
        "message": "Test Started",
        "target": f"{ip}:{port}",
        "players": players,
        "duration": f"{duration}s"
    }

@app.get("/status")
async def get_status():
    return stats
    
