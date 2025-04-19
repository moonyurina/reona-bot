import discord
from discord.ext import commands, tasks
import datetime
import json
import os
from datetime import datetime as dt, timedelta

# ━━━━━━━━━━━━━━━━━━━━━━━━
# 💦 レオナの淫乱変態設定ゾーン（でかまら起動準備）
# ━━━━━━━━━━━━━━━━━━━━━━━━
TOKEN = os.getenv("DISCORD_TOKEN")

# 🔥 本番モード（濃厚フタナリ汁が飛び交う）
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

def get_now_utc():
    return dt.utcnow()

@bot.event
async def on_ready():
    global startup_time
    startup_time = dt.utcnow()

    now = startup_time + timedelta(hours=9)
    print(f"[レオナBOT] 起動処理開始！現在のモードは {MODE}")
    print(f"[レオナBOT] startup_time（UTC）→ {startup_time.isoformat()}")
    log_channel = None
    try:
        log_channel = await bot.fetch_channel(get_log_channel_id())
        print(f"[レオナBOT] ログチャンネル取得成功 → ID: {get_log_channel_id()} | オブジェクト: {log_channel}")
        if log_channel:
            await log_channel.send(f"🚀 [{now.strftime('%Y-%m-%d %H:%M:%S')}] レオナBOT起動完了（モード: {MODE}）…ボーボー腋毛スタンバイ中♡")
            await log_channel.send(f"🔁 [{now.strftime('%Y-%m-%d %H:%M:%S')}] Resume Web Service 開始（モード: {MODE}）…腋汗とチン臭全開で見張ってるよ♡")
        else:
            print("[レオナBOT] ⚠️ ログチャンネルがNoneやで…IDミスかBOTの権限不足かも！")
    except Exception as e:
        print(f"[レオナBOT] ログチャンネル取得・送信時のエラー: {e}")

    if MODE == "TEST":
        check_loop.change_interval(seconds=10)
    check_loop.start()

@tasks.loop(minutes=1)
async def check_loop():
    now = dt.utcnow() + timedelta(hours=9)
    if MODE == "NORMAL" and now.hour != 3:
        return
    await check_once()

async def check_once():
    data = load_data()
    now_jst = dt.utcnow() + timedelta(hours=9)
    now_utc = dt.utcnow()
    updated = False
    deleted_count = 0
    new_mirrors = 0

    source_channel = await bot.fetch_channel(get_source_channel_id())
    mirror_channel = await bot.fetch_channel(get_mirror_channel_id())
    log_channel = await bot.fetch_channel(get_log_channel_id())

    messages = [msg async for msg in source_channel.history(limit=10)]
    new_data = {}

    for msg in messages:
        if msg.author.bot:
            continue
        mid = str(msg.id)
        ts = msg.created_at.replace(tzinfo=None)
        if mid not in data and startup_time and ts >= startup_time:
            expire_date = (now_jst + timedelta(days=30)).strftime('%Y-%m-%d %H:%M')
            tag = "#Only10Sec" if MODE == "TEST" else "#Only30Days"
            content = msg.content + f"\n\n{tag}\n🗓️ This image will self-destruct on {expire_date}"
            files = [await a.to_file() for a in msg.attachments]
            mirror = await mirror_channel.send(content, files=files)
            new_data[mid] = {
                "mirror_id": mirror.id,
                "timestamp": dt.utcnow().isoformat(),
                "expire_date": expire_date,
                "deleted": False
            }
            updated = True
            new_mirrors += 1
        elif mid in data and not data[mid].get("deleted"):
            new_data[mid] = data[mid]

    for mid, info in list(new_data.items()):
        if info.get("deleted"):
            continue
        ts = dt.fromisoformat(info["timestamp"])
        expired = (now_utc - ts).total_seconds() >= 10 if MODE == "TEST" else (now_utc - ts).days >= 30
        if expired:
            try:
                msg = await mirror_channel.fetch_message(int(info["mirror_id"]))
                deletion_notice = f"🗑️ This image was deleted on {info['expire_date']}"
                await msg.edit(content=deletion_notice, attachments=[])
                info["deleted"] = True
                updated = True
                deleted_count += 1
            except Exception as e:
                print(f"[レオナBOT] 削除エラー: {e}")

    if updated:
        save_data(new_data)

    if log_channel:
        try:
            if new_mirrors == 0 and deleted_count == 0:
                await log_channel.send(f"📭 [{now_jst.strftime('%Y-%m-%d %H:%M:%S')}] （モード: {MODE}）今日は濃いのゼロ…腋毛こすっただけだったわ…💦")
            elif new_mirrors > 0 and deleted_count == 0:
                await log_channel.send(f"📥 [{now_jst.strftime('%Y-%m-%d %H:%M:%S')}] （モード: {MODE}）{new_mirrors}件ミラー完了♡ レオナのデカマラで保存しておいたわよ♡")
            elif deleted_count > 0:
                await log_channel.send(f"🧻 [{now_jst.strftime('%Y-%m-%d %H:%M:%S')}] （モード: {MODE}）{deleted_count}件分、濃厚ザーメン全部お掃除完了♡ 次のオナペ、準備しときな♡")
        except Exception as e:
            print(f"[レオナBOT] ログ出力エラー: {e}")

def get_source_channel_id():
    return TEST_SOURCE_CHANNEL_ID if MODE == "TEST" else NORMAL_SOURCE_CHANNEL_ID

def get_mirror_channel_id():
    return TEST_MIRROR_CHANNEL_ID if MODE == "TEST" else NORMAL_MIRROR_CHANNEL_ID

def get_log_channel_id():
    return LOG_CHANNEL_ID

bot.run(TOKEN)
