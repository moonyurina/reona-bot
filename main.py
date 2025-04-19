import discord
from discord.ext import commands, tasks
import datetime
import json
import os
from datetime import datetime as dt, timedelta

# ---------- 設定 ----------
TOKEN = os.getenv("DISCORD_TOKEN")
SOURCE_CHANNEL_ID = 1350654751553093692  # 💦 投稿元チャンネルID（レオナが見張ってるエリアだよ）
MIRROR_CHANNEL_ID = 1362400364069912606  # 💦 ミラー投稿先チャンネルID（濃いやつはここにぶち込む♡）
LOG_CHANNEL_ID = 1362964804658003978     # 💦 ログ投稿チャンネルID（レオナの報告会場だね）
DATA_FILE = "data.json"

# 🔧 モード選択（レオナの勤務スタイル切替♡）
# NORMAL → 毎日3時にちんぽチェック💦
# TEST → 10秒ごとにぶっこきテスト確認♡（ちょっとした興奮確認モード）
MODE = "TEST"  # ← ← ← 🔄 ここを "NORMAL" にするとお仕事本番💪
# --------------------------

# 🧠 レオナの感知能力（意識）をONにして、投稿の内容を舐め回すように読む準備♡
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 🍑 保存してる濃厚投稿データを読み込み

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# 🍌 データ保存（レオナのメモ帳に書き込み）
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# 🔥 起動したときの処理（ちんぽミルク補充完了♡）
@bot.event
async def on_ready():
    now = dt.utcnow() + timedelta(hours=9)
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    print(f"[レオナBOT] 起動完了…ちんぽミルク満タンで待機中…💦")
    if log_channel:
        await log_channel.send(f"🚀 [{now.strftime('%Y-%m-%d %H:%M:%S')}] レオナBOT起動完了…ちんぽミルク満タンで待機中…💦")
        await log_channel.send(f"🔁 [{now.strftime('%Y-%m-%d %H:%M:%S')}] Resume Web Service 開始したよ…濃いの、ぶち込む準備できてるからな♡")
    if MODE == "TEST":
        check_loop.change_interval(seconds=10)  # 💦 テストモードでは10秒ごとの発射チェック♡
    check_loop.start()

# 🔁 モードに応じて実行ループを切り替える（筋トレかオナニーか選ぶ感じ）
@tasks.loop(minutes=1)
async def check_loop():
    now = dt.utcnow() + timedelta(hours=9)
    if MODE == "NORMAL" and now.hour != 3:
        return
    await check_once()

# 💦 ミラー投稿＆削除チェック（レオナの汗だく濃厚業務♡）
async def check_once():
    data = load_data()
    now = dt.utcnow() + timedelta(hours=9)
    updated = False
    deleted_count = 0
    new_mirrors = 0

    source_channel = bot.get_channel(SOURCE_CHANNEL_ID)
    mirror_channel = bot.get_channel(MIRROR_CHANNEL_ID)
    log_channel = bot.get_channel(LOG_CHANNEL_ID)

    if source_channel:
        messages = await source_channel.history(limit=10).flatten()
        for message in messages:
            if not message.author.bot and str(message.id) not in data:
                expire_date = (now + timedelta(days=30)).strftime('%Y-%m-%d %H:%M')
                content = message.content + f"\n\n#Only30Days\n🗓️ This image will self-destruct on {expire_date}"
                files = [await a.to_file() for a in message.attachments]
                mirror = await mirror_channel.send(content, files=files)
                data[str(message.id)] = {
                    "mirror_id": mirror.id,
                    "timestamp": dt.utcnow().isoformat(),
                    "expire_date": expire_date
                }
                updated = True
                new_mirrors += 1
                print(f"[レオナBOT] ミラー投稿完了: {mirror.id}")

    for original_id, info in list(data.items()):
        ts = dt.fromisoformat(info["timestamp"])
        if MODE == "TEST":
            expired = (now - ts).total_seconds() >= 10
        else:
            expired = (now - ts).days >= 30

        if expired:
            try:
                msg = await mirror_channel.fetch_message(int(info["mirror_id"]))
                original_content = msg.content.split('\n\n🗓️')[0].replace("#Only30Days", "").strip()
                deletion_notice = f"\n\n🗑️ This image was deleted on {info['expire_date']}"  # 💦 削除されたことをしっかり伝える♡
                await msg.edit(content=original_content + deletion_notice, attachments=[])
                del data[original_id]
                updated = True
                deleted_count += 1
                print(f"[レオナBOT] {info['mirror_id']} のちんぽ汁、ふき取ったぜ…💦")
            except Exception as e:
                print(f"[レオナBOT] エラー発射: {e}")

    if updated:
        save_data(data)

    if log_channel:
        if new_mirrors == 0 and deleted_count == 0:
            await log_channel.send(f"📭 [{now.strftime('%Y-%m-%d %H:%M:%S')}] 😤 レオナだよ…くっ、今日は追加も削除も無し…ムダに汗かいただけじゃん…💦")
        elif new_mirrors > 0 and deleted_count == 0:
            await log_channel.send(f"📥 [{now.strftime('%Y-%m-%d %H:%M:%S')}] 💪 フゥ…{new_mirrors}件ぶち込んだけど、まだ30日経ってないからそのまま放置だよ…見逃すなよぉ♡")
        elif deleted_count > 0:
            await log_channel.send(f"🧻 [{now.strftime('%Y-%m-%d %H:%M:%S')}] 💦 {deleted_count}件分、しっかりふき取ったからな…次の濃い投稿、楽しみにしてるぜ♡")

# 🍑 Renderのスケジュール実行前提で、常駐せず即座に濃厚対応してイキます
bot.run(TOKEN)
