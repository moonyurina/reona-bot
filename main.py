import discord
from discord.ext import commands
import datetime
import json
import os
from datetime import datetime as dt, timedelta

# ---------- 設定 ----------
TOKEN = os.getenv("DISCORD_TOKEN")
SOURCE_CHANNEL_ID = 1350654751553093692  # 投稿元チャンネルID
MIRROR_CHANNEL_ID = 1362400364069912606  # ミラー投稿先チャンネルID
LOG_CHANNEL_ID = 1362964804658003978  # ✅ ログ用チャンネルID
DATA_FILE = "data.json"
# --------------------------

# DiscordのIntent設定（メッセージ内容の取得を有効化）
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# JSONファイルからミラーデータを読み込む
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


# ミラーデータを保存
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


# Bot起動時の処理
@bot.event
async def on_ready():
    now = dt.utcnow() + timedelta(hours=9)
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    print(f"[レオナBOT] 起動完了…ちんぽミルク満タンで待機中…💦")
    if log_channel:
        await log_channel.send(
            f"🚀 [{now.strftime('%Y-%m-%d %H:%M:%S')}] レオナBOT起動完了…ちんぽミルク満タンで待機中…💦"
        )
        await log_channel.send(
            f"🔁 [{now.strftime('%Y-%m-%d %H:%M:%S')}] Resume Web Service 開始したよ…濃いの、ぶち込む準備できてるからな♡"
        )
    await check_once(force=True)  # 🔥 起動時は強制実行
    await bot.close()


# 実際の処理（ミラー＆削除チェック）
async def check_once(force=False):
    data = load_data()
    now = dt.utcnow() + timedelta(hours=9)  # JST
    updated = False
    deleted_count = 0
    new_mirrors = 0

    source_channel = bot.get_channel(SOURCE_CHANNEL_ID)
    mirror_channel = bot.get_channel(MIRROR_CHANNEL_ID)
    log_channel = bot.get_channel(LOG_CHANNEL_ID)

    # 🔽 最新のメッセージ10件を取得して新規投稿をミラー
    if source_channel:
        messages = await source_channel.history(limit=10).flatten()
        for message in messages:
            if not message.author.bot and str(message.id) not in data:
                expire_date = (now +
                               timedelta(days=30)).strftime('%Y-%m-%d %H:%M')
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

    # 🔽 30日経過したミラー投稿をチェック（force=True の場合は必ず実行）
    if force or now.hour == 3:
        for original_id, info in list(data.items()):
            ts = dt.fromisoformat(info["timestamp"])
            if (now - ts).days >= 30:
                try:
                    msg = await mirror_channel.fetch_message(
                        int(info["mirror_id"]))
                    original_content = msg.content.split('\n\n🗓️')[0].replace(
                        "#Only30Days", "").strip()
                    deletion_notice = f"\n\n🗑️ This image was deleted on {info['expire_date']}"
                    await msg.edit(content=original_content + deletion_notice,
                                   attachments=[])
                    del data[original_id]
                    updated = True
                    deleted_count += 1
                    print(f"[レオナBOT] {info['mirror_id']} のちんぽ汁、ふき取ったぜ…💦")
                except Exception as e:
                    print(f"[レオナBOT] エラー発射: {e}")

    if updated:
        save_data(data)

    # 🔔 ログ出力（レオナ風）
    if log_channel:
        if new_mirrors == 0 and deleted_count == 0:
            await log_channel.send(
                f"📭 [{now.strftime('%Y-%m-%d %H:%M:%S')}] 😤 レオナだよ…くっ、今日は追加も削除も無し…ムダに汗かいただけじゃん…💦"
            )
        elif new_mirrors > 0 and deleted_count == 0:
            await log_channel.send(
                f"📥 [{now.strftime('%Y-%m-%d %H:%M:%S')}] 💪 フゥ…{new_mirrors}件ぶち込んだけど、まだ30日経ってないからそのまま放置だよ…見逃すなよぉ♡"
            )
        elif deleted_count > 0:
            await log_channel.send(
                f"🧻 [{now.strftime('%Y-%m-%d %H:%M:%S')}] 💦 {deleted_count}件分、しっかりふき取ったからな…次の濃い投稿、楽しみにしてるぜ♡"
            )


# 実行（RenderのScheduled Jobから起動想定）
bot.run(TOKEN)
