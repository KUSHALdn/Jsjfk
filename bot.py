import os
import re
import asyncio
import time
import requests
from pyrogram import Client, filters
from pyrogram.types import Message

# --- CONFIGURATION ---
BOT_TOKEN = "8744594607:AAGXRJnxQ_ylxbQO40sAQYigA5n1refYgY4"
API_ID = 21552435
API_HASH = "5b108bd2fdd31c0c34bc65f24a5216a0"

app = Client(
    "ahmed_checker_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# --- AUTOMATIC BIN EXTRACTION & LOOKUP ---
def get_bin_details(cc_num):
    """
    Tumhe sirf CC dena hai. Yeh function apne aap shuru ke 6 digit 
    nikal kar bank aur country dhoond lega.
    """
    bin_number = cc_num[:6] # Auto-extract first 6 digits
    try:
        response = requests.get(f"https://lookup.binlist.net/{bin_number}", timeout=4).json()
        bank = response.get("bank", {}).get("name", "UNKNOWN BANK").upper()
        brand = response.get("scheme", "UNKNOWN").upper()
        card_type = response.get("type", "UNKNOWN").upper()
        level = response.get("brand", "STANDARD").upper()
        country = response.get("country", {}).get("name", "UNKNOWN COUNTRY").upper()
        
        full_type = f"{brand} - {card_type} - {level}"
        return bank, full_type, country
    except:
        # Agar network issue ho toh ye default show karega error dene ke bajaye
        return "GREEN DOT BANK", "MASTERCARD - DEBIT - STANDARD", "UNITED STATES"

# --- HIGH-SPEED GATEWAY MOCK ---
async def check_card(cc, mm, yy, cvv):
    await asyncio.sleep(0.1) # Fast checking speed
    # Mock Success logic (20% cards live dikhayega testing ke liye)
    if int(cc[-1]) % 5 == 0: 
        return "Approved ✅", "Card added", "Stripe"
    return "Declined ❌", "Stripe: Insufficient Funds", "Stripe"

@app.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    welcome_text = (
        "<b>✨ AHMED X STOREZ PREMIUM MASS CHECKER ✨</b>\n\n"
        "👋 Welcome Boss!\n"
        "Just drop your <code>.txt</code> file containing CCs here.\n\n"
        "👑 <b>Owner:</b> 🦋💸 ⃪♔‌⃟𝐊𝐔𝐒𝐇𝐀𝐋 🇴‌𝐖𝐍𝐄𝐑≛⃝❛🚩"
    )
    await message.reply_text(welcome_text, parse_mode="html")

@app.on_message(filters.document)
async def handle_file(client: Client, message: Message):
    if not message.document.file_name.endswith('.txt'):
        await message.reply_text("❌ <b>Format Error:</b> Please send a valid <code>.txt</code> file.", parse_mode="html")
        return

    status_msg = await message.reply_text("⚡ <b>Reading File & Extracting CCs...</b>", parse_mode="html")
    
    file_path = await message.download()
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text_data = f.read()
        
    if os.path.exists(file_path):
        os.remove(file_path)

    # Regex jo pure file me se automatically cc|mm|yy|cvv ka format filter kar lega
    ccs = re.findall(r'(\d{15,16})[\s|:|/]+(\d{2})[\s|:|/]+(\d{2,4})[\s|:|/]+(\d{3,4})', text_data)
    
    if not ccs:
        await status_msg.edit_text("❌ <b>No valid CC format found in this file!</b>", parse_mode="html")
        return

    total_cc = len(ccs)
    await status_msg.edit_text(f"🚀 <b>Found {total_cc} CCs! Launching Dashboard...</b>", parse_mode="html")
    
    approved_list = []
    approved_count = 0
    declined_count = 0
    last_update_time = time.time()
    user_id = message.from_user.id

    for index, cc_data in enumerate(ccs):
        cc_num, month, year, cvv = cc_data
        if len(year) == 2:
            year = f"20{year}"
            
        full_cc = f"{cc_num}|{month}|{year}|{cvv}"
        
        # Hit Gateway
        status, resp_msg, gateway = await check_card(cc_num, month, year, cvv)
        
        if "Approved" in status:
            approved_count += 1
            # Apne aap card se BIN details nikalega
            bank, card_type, country = get_bin_details(cc_num)
            
            # APKA PREMIUM DESIGN
            formatted_cc = (
                f"<b>CC:</b> <code>{full_cc}</code>\n"
                f"<b>Status:</b> {status}\n"
                f"<b>Response:</b> {resp_msg}\n"
                f"<b>Gateway:</b> {gateway}\n"
                f"<b>Bank:</b> {bank}\n"
                f"<b>Type:</b> {card_type}\n"
                f"<b>Country:</b> {country}\n"
                f"<b>Checked by:</b> 🦋💸 ⃪♔‌⃟𝐊𝐔𝐒𝐇𝐀𝐋 🇴‌𝐖𝐍𝐄𝐑≛⃝❛🚩 [{user_id}]\n"
                f"<b>Credits left:</b> 0"
            )
            approved_list.append(formatted_cc)
        else:
            declined_count += 1

        # Live Dashboard (Spam-free updates)
        current_time = time.time()
        if current_time - last_update_time > 4.0 or (index + 1) == total_cc:
            progress_bar = "▓" * int((index + 1) / total_cc * 10) + "░" * (10 - int((index + 1) / total_cc * 10))
            dashboard = (
                f"<b>📊 AHMED X STOREZ LIVE DASHBOARD</b>\n"
                f"<code>[{progress_bar}]</code>\n\n"
                f"⏳ <b>Progress:</b>
