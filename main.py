import asyncio
import socket
import time
import os

TARGET_IP = input("IP: ")
TARGET_PORT = int(input("PORT: "))
PLAYERS = int(input("Players: "))
DURATION = int(input("Duration: "))

sent = 0
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

async def player_sim():
    global sent

    end_time = time.time() + DURATION

    while time.time() < end_time:
        try:
            data = os.urandom(64)  # small packet

            sock.sendto(data, (TARGET_IP, TARGET_PORT))
            sent += 1

        except:
            pass

        await asyncio.sleep(0.05)

async def main():
    print("\n🚀 Running Load Test...\n")

    tasks = [asyncio.create_task(player_sim()) for _ in range(PLAYERS)]
    await asyncio.gather(*tasks)

    print("\n📊 RESULT")
    print(f"Packets Sent: {sent}")

    sock.close()

asyncio.run(main())
