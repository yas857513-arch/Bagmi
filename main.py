from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import time
import random

app = FastAPI()

# CORS fix (important for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Backend Running"}

@app.get("/run-test")
async def run_test(players: int = 10, duration: int = 5):
    counter = 0

    async def player_sim():
        nonlocal counter
        end_time = time.time() + duration

        while time.time() < end_time:
            # safe simulation
            fake = random.randint(1, 100)
            _ = fake * fake
            counter += 1
            await asyncio.sleep(0.05)

    tasks = [asyncio.create_task(player_sim()) for _ in range(players)]
    await asyncio.gather(*tasks)

    return {
        "players": players,
        "duration": duration,
        "operations": counter
    }
