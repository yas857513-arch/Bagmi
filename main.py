import asyncio
import socket
import os
import time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- CONFIGURATION ---
# Use Environment Variables for security
API_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- STATES ---
class TestStates(StatesGroup):
    waiting_for_ip = State()
    waiting_for_port = State()
    waiting_for_players = State()
    waiting_for_duration = State()

# --- YOUR ORIGINAL LOGIC (Integrated) ---
async def run_load_test(ip, port, players, duration, message: types.Message):
    sent = 0
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    async def player_sim():
        nonlocal sent
        end_time = time.time() + duration
        while time.time() < end_time:
            try:
                data = os.urandom(64)
                sock.sendto(data, (ip, port))
                sent += 1
            except:
                pass
            await asyncio.sleep(0.05) # Keeps your original timing

    tasks = [asyncio.create_task(player_sim()) for _ in range(players)]
    
    # Progress Update Task
    async def report_progress():
        while any(not t.done() for t in tasks):
            await asyncio.sleep(3)
            try:
                await message.edit_text(f"🚀 **Test in Progress...**\nPackets sent: `{sent}`")
            except: pass

    reporter = asyncio.create_task(report_progress())
    await asyncio.gather(*tasks)
    reporter.cancel()
    sock.close()
    return sent

# --- TELEGRAM HANDLERS ---
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer("🎯 **Network Load Tester**\nSend the **Target IP** to begin:")
    await state.set_state(TestStates.waiting_for_ip)

@dp.message(TestStates.waiting_for_ip)
async def get_ip(message: types.Message, state: FSMContext):
    await state.update_data(ip=message.text)
    await message.answer("Enter **Port**:")
    await state.set_state(TestStates.waiting_for_port)

@dp.message(TestStates.waiting_for_port)
async def get_port(message: types.Message, state: FSMContext):
    await state.update_data(port=int(message.text))
    await message.answer("Enter **Players** (Threads):")
    await state.set_state(TestStates.waiting_for_players)

@dp.message(TestStates.waiting_for_players)
async def get_players(message: types.Message, state: FSMContext):
    await state.update_data(players=int(message.text))
    await message.answer("Enter **Duration** (seconds):")
    await state.set_state(TestStates.waiting_for_duration)

@dp.message(TestStates.waiting_for_duration)
async def finalize(message: types.Message, state: FSMContext):
    data = await state.get_data()
    duration = int(message.text)
    
    status_msg = await message.answer("⏳ Initializing test...")
    
    total_sent = await run_load_test(data['ip'], data['port'], data['players'], duration, status_msg)
    
    await status_msg.edit_text(f"📊 **RESULT**\nTarget: `{data['ip']}`\nPackets Sent: `{total_sent}`")
    await state.clear()

async def main():
    print("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
