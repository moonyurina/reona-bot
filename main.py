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
    print(f"[レオナBOT] 起動完了…ちんぽミルク満タンで待機中…💦")
    await check_once()  # 🔥 毎日3時にRenderのScheduled Jobから呼ばれる想定で1回だけ実行
    await bot.close()   # ✅ 実行後にBOTを終了（常駐しない）

# 実際の処理（ミラー＆削除チェック）
async def check_once():
    data = load_data()
    now = dt.utcnow() + timedelta(hours=9)  # JST時間に変換
    updated = False

    # ミラー元チャンネルの取得
    source_channel = bot.get_channel(SOURCE_CHANNEL_ID)
    mirror_channel = bot.get_channel(MIRROR_CHANNEL_ID)

    # 🔽 最新のメッセージ10件を取得して新規投稿をミラー
    if source_channel:
        messages = await source_channel.history(limit=10).flatten()
        for message in messages:
            if not message.author.bot and str(message.id) not in data:
                expire_date = (now + timedelta(days=30)).strftime('%Y-%m-%d %H:%M')
                # 📝 投稿ミラー時のコメント
                # 英語: This image will self-destruct on {expire_date}
                # 日本語: この画像は {expire_date} に自動で消滅します
                content = message.content + f"\n\n#Only30Days\n🗓️ This image will self-destruct on {expire_date}"
                files = [await a.to_file() for a in message.attachments]
                mirror = await mirror_channel.send(content, files=files)
                # オリジナルメッセージIDをキーとして記録
                data[str(message.id)] = {
                    "mirror_id": mirror.id,
                    "timestamp": dt.utcnow().isoformat(),
                    "expire_date": expire_date
                }
                updated = True
                print(f"[レオナBOT] ミラー投稿完了: {mirror.id}")

    # 🔽 30日経過したミラー投稿をチェックして画像削除＆コメント更新
    for original_id, info in list(data.items()):
        ts = dt.fromisoformat(info["timestamp"])
        if (now - ts).days >= 30:
            try:
                msg = await mirror_channel.fetch_message(int(info["mirror_id"]))
                original_content = msg.content.replace("#Only30Days", "").strip()
                # 削除コメントを1種類に統一
                # 英語: This image was deleted on {expire_date}
                # 日本語: この画像は {expire_date} に削除されました
                deletion_notice = f"\n\n🗑️ This image was deleted on {info['expire_date']}"
                await msg.edit(content=original_content + deletion_notice, attachments=[])
                del data[original_id]
                updated = True
                print(f"[レオナBOT] {info['mirror_id']} のちんぽ汁、ふき取ったぜ…💦")
            except Exception as e:
                print(f"[レオナBOT] エラー発射: {e}")

    if updated:
        save_data(data)

# 実行（RenderのScheduled Jobから起動想定）
bot.run(TOKEN)