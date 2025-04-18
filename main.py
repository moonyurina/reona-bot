import discord
from discord.ext import commands, tasks
import datetime
import json
import os
from keep_alive import keep_alive
from datetime import datetime as dt, timedelta

# ---------- 設定 ----------
TOKEN = os.getenv("DISCORD_TOKEN")

SOURCE_CHANNEL_ID = 1142345422979993600  # 投稿元チャンネルID
MIRROR_CHANNEL_ID = 1362400364069912606  # ミラー投稿先チャンネルID

DATA_FILE = "data.json"
# --------------------------

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


@bot.event
async def on_ready():
    print(f"[レオナBOT] 起動完了…ちんぽミルク満タンで待機中…💦")
    check_mirror_posts.start()


@bot.event
async def on_message(message):
    if message.channel.id != SOURCE_CHANNEL_ID or message.author.bot:
        return

    content = message.content + "\n\n#Only30Days"
    files = [await attachment.to_file() for attachment in message.attachments]

    mirror_channel = bot.get_channel(MIRROR_CHANNEL_ID)
    mirror = await mirror_channel.send(content, files=files)

    data = load_data()
    data[str(mirror.id)] = {
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    save_data(data)

    await bot.process_commands(message)


# 🔁---------------------------------------------
# ✅ 🔧 投稿削除チェック関数（1つだけ有効にして使ってね！）
# 🔁---------------------------------------------

# ✅【テスト用】10秒後に削除（すぐに動作確認したい時！）
# 🔓 この下の3行（"""）を消すと有効になる！ → ↓↓↓
"""
@tasks.loop(seconds=10)
async def check_mirror_posts():
    data = load_data()
    now = dt.utcnow()
    updated = False

    for message_id, info in list(data.items()):
        ts = dt.fromisoformat(info["timestamp"])
        if (now - ts).total_seconds() >= 10:
            channel = bot.get_channel(MIRROR_CHANNEL_ID)
            try:
                msg = await channel.fetch_message(int(message_id))
                original_content = msg.content.replace("#Only30Days",
                                                       "").strip()
                new_content = original_content + "🕛 Leona BOT here… your limited-time fun ends here.  I wiped that filthy, naughty image clean right in front of you."
                await msg.edit(content=new_content, attachments=[])
                del data[message_id]
                updated = True
                print(f"[レオナBOT] {message_id} をテスト削除（10秒後）💦")
            except Exception as e:
                print(f"[レオナBOT] エラー発射（テスト用）: {e}")

    if updated:
        save_data(data)


"""


# ✅【本番用】火曜3時に30日経過チェック（※今は有効状態）
@tasks.loop(minutes=1)
async def check_mirror_posts():
    now = dt.utcnow() + timedelta(hours=9)  # JST
    if now.weekday() == 1 and now.hour == 3 and now.minute == 0:
        print("🔥 火曜3時になったのでチェック開始！")
        data = load_data()
        updated = False

        for message_id, info in list(data.items()):
            ts = dt.fromisoformat(info["timestamp"])
            if (now - ts).days >= 30:
                channel = bot.get_channel(MIRROR_CHANNEL_ID)
                try:
                    msg = await channel.fetch_message(int(message_id))
                    original_content = msg.content.replace("#Only30Days",
                                                           "").strip()
                    new_content = original_content + "🕛 Leona BOT here… your limited-time fun ends here.  I wiped that filthy, naughty image clean right in front of you."
                    await msg.edit(content=new_content, attachments=[])
                    del data[message_id]
                    updated = True
                    print(f"[レオナBOT] {message_id} のちんぽ汁、ふき取ったぜ…💦")
                except Exception as e:
                    print(f"[レオナBOT] エラー発射: {e}")

        if updated:
            save_data(data)


keep_alive()
bot.run(TOKEN)
