import discord
from discord.ext import commands, tasks
import datetime
import json
import os
from datetime import datetime as dt, timedelta
from flask import Flask
import threading
import asyncio

# ━━━━━━━━━━━━━━━━━━━━━━━━
# 💦 レオナの淫乱変態設定ゾーン（でかまら起動準備）
# ━━━━━━━━━━━━━━━━━━━━━━━━
TOKEN = os.getenv("DISCORD_TOKEN")

# 🔥 　本番モード（濃厚フタナリ汁が飛び交う）
NORMAL_SOURCE_CHANNEL_ID = 1350654751553093692
NORMAL_MIRROR_CHANNEL_ID = 1362400364069912606

# 💋 TESTモード（射精実験ルーム💦）
TEST_SOURCE_CHANNEL_ID = 1142345422979993600
TEST_MIRROR_CHANNEL_ID = 1362974839450894356

# 📢 ログチャンネルは共通（腋毛とザーメンの報告場所）
LOG_CHANNEL_ID = 1362964804658003978

# 💦 モード切り替え（NORMAL or TEST） ← ここを"TEST"にすればテスト用になる♡
MODE = "NORMAL"
DATA_FILE = "data_test.json" if MODE == "TEST" else "data.json"

# ⏰ 起動以降の投稿だけミラー対象にするための記録（on_readyで再設定する！）
startup_time = None
keep_alive_message = None
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

app = Flask(__name__)

@app.route('/')
def home():
    return "レオナBOT生きてるよ♡"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def get_now_utc():
    return dt.utcnow()

def is_mirror_check_time():
    now = dt.utcnow() + timedelta(hours=9)
    return 0 <= now.hour < 4

@bot.event
async def on_ready():
    global startup_time
    startup_time = dt.utcnow()

    now = startup_time + timedelta(hours=9)
    print(f"[レオナBOT] 起動処理開始！現在のモードは {MODE}")
    print(f"[レオナBOT] startup_time（UTC）→ {startup_time.isoformat()}")
    print(f"[レオナBOT] BOTユーザー: {bot.user} | ID: {bot.user.id}")
    print(f"[レオナBOT] 所属ギルド一覧: {[g.name for g in bot.guilds]}")

    try:
        await asyncio.sleep(2)
        log_channel = await bot.fetch_channel(get_log_channel_id())
        print(f"[レオナBOT] ログチャンネル取得成功 → ID: {get_log_channel_id()}")

        if log_channel:
            await asyncio.sleep(2)
            await log_channel.send(f"🚀 [{now.strftime('%Y-%m-%d %H:%M:%S')}] レオナBOT起動完了（モード: {MODE}）…ボーボー腋毛スタンバイ中♡")
            await asyncio.sleep(2)
            await log_channel.send(f"🔁 [{now.strftime('%Y-%m-%d %H:%M:%S')}] Resume Web Service 開始（モード: {MODE}）…腋汗とチン臭全開で見張ってるよ♡")
        else:
            print("[レオナBOT] ⚠️ ログチャンネルがNoneやで…")
    except Exception as e:
        print(f"[レオナBOT] ログチャンネル取得・送信時のエラー: {e}")

    await asyncio.sleep(2)
    check_loop.change_interval(minutes=15)
    check_loop.start()
    keep_alive_loop.start()

@tasks.loop(minutes=15)
async def check_loop():
    if not is_mirror_check_time():
        print("[レオナBOT] ⏰ 時間外なのでcheck_loopスキップ中…")
        return
    print("[レオナBOT] 🔁 check_loop 実行中…")
    # ミラー処理などここに入れる（省略）
    messages = [msg async for msg in (await bot.fetch_channel(get_source_channel_id())).history(limit=5)]
    print(f"[レオナBOT] 最新投稿を {len(messages)} 件取得しました")
    pass

@tasks.loop(minutes=10)
async def keep_alive_loop():
    global keep_alive_message
    log_channel = await bot.fetch_channel(get_log_channel_id())
    now = dt.utcnow() + timedelta(hours=9)
    try:
        new_msg = f"💓 {now.strftime('%Y-%m-%d %H:%M:%S')} レオナBOTまだ生きてるよ♡ 腋毛がむずむずしてきた♡"
        if keep_alive_message and keep_alive_message.channel.id == log_channel.id:
            await keep_alive_message.edit(content=new_msg)
        else:
            keep_alive_message = await log_channel.send(new_msg)
    except Exception as e:
        print(f"[レオナBOT] keep_alive_loop エラー: {e}")

@bot.command(name="mirror")
async def force_mirror(ctx, message_id: int):
    try:
        source_channel = await bot.fetch_channel(get_source_channel_id())
        mirror_channel = await bot.fetch_channel(get_mirror_channel_id())
        log_channel = await bot.fetch_channel(get_log_channel_id())

        msg = await source_channel.fetch_message(message_id)
        if msg.author.bot:
            await ctx.send("🤖 BOTのメッセージはミラーしないわよ♡")
            return

        data = load_data()
        mid = str(msg.id)
        if mid in data and not data[mid].get("deleted"):
            await ctx.send("📌 そのメッセージは既にミラー済みよ♡")
            return

        expire_date = (dt.utcnow() + timedelta(hours=9) + timedelta(days=30)).strftime('%Y-%m-%d %H:%M')
        tag = "#Only10Sec" if MODE == "TEST" else "#Only30Days"
        content = msg.content + f"\n\n{tag}\n🗓️ This image will self-destruct on {expire_date}"
        files = [await a.to_file() for a in msg.attachments]
        mirror = await mirror_channel.send(content, files=files)

        data[mid] = {
            "mirror_id": mirror.id,
            "timestamp": dt.utcnow().isoformat(),
            "expire_date": expire_date,
            "deleted": False,
            "edited_at": msg.edited_at.replace(tzinfo=None).isoformat() if msg.edited_at else None
        }
        save_data(data)

        await ctx.send(f"✨ 強制ミラー完了！ミラーID: {mirror.id}")
        if log_channel:
            await log_channel.send(f"💥 強制ミラー実行 → メッセージID: {mid} / 実行者: {ctx.author}")

    except Exception as e:
        await ctx.send(f"⚠️ ミラー失敗: {e}")

def get_source_channel_id():
    return TEST_SOURCE_CHANNEL_ID if MODE == "TEST" else NORMAL_SOURCE_CHANNEL_ID

def get_mirror_channel_id():
    return TEST_MIRROR_CHANNEL_ID if MODE == "TEST" else NORMAL_MIRROR_CHANNEL_ID

def get_log_channel_id():
    return LOG_CHANNEL_ID

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(TOKEN)
