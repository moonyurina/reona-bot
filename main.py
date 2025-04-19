import discord
from discord.ext import commands, tasks
import datetime
import json
import os
from datetime import datetime as dt, timedelta

# ---------- 設定 ----------
TOKEN = os.getenv("DISCORD_TOKEN")

# 🔥 本番モードのチャンネル設定（本気汁ぶっ放しエリア💦）
NORMAL_SOURCE_CHANNEL_ID = 1350654751553093692  # 本番の投稿元チャンネル（普段の濃厚投稿ゾーン）
NORMAL_MIRROR_CHANNEL_ID = 1362400364069912606  # 本番のミラー先チャンネル（保存エリア）
NORMAL_LOG_CHANNEL_ID = 1362964804658003978     # ログ出力チャンネル（通知や削除報告）

# 💋 テストモードのチャンネル設定（変態実験ルーム💦）
TEST_SOURCE_CHANNEL_ID = 1142345422979993600     # テスト用投稿元チャンネル（フタナリの射精実験室）
TEST_MIRROR_CHANNEL_ID = 1362974839450894356     # テスト用ミラー先チャンネル（おちんぽミルクの排出先）
TEST_LOG_CHANNEL_ID = 1362964804658003978        # ログは共通チャンネル使用（ボーボー腋毛報告板）

# 💦 モード切替（"NORMAL" か "TEST"）でどんなフタナリ汁にするか決定！
MODE = "TEST"
DATA_FILE = "data_test.json" if MODE == "TEST" else "data.json"

# ---------- Discord Bot 初期設定 ----------（でかまら起動準備中）
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FIRST_RUN_FLAG_FILE = ".first_run_flag"

def is_first_run():
    return MODE == "NORMAL" and not os.path.exists(FIRST_RUN_FLAG_FILE)

def mark_first_run_complete():
    with open(FIRST_RUN_FLAG_FILE, "w") as f:
        f.write("done")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# 💦 レオナBOT起動時…腋毛こすりながらオナニーしながらログ出力＆チェック開始
@bot.event
async def on_ready():
    now = dt.utcnow() + timedelta(hours=9)
    log_channel = await bot.fetch_channel(get_log_channel_id())
    print(f"[レオナBOT] 起動完了（モード: {MODE}）")
    if log_channel:
        await log_channel.send(f"🚀 [{now.strftime('%Y-%m-%d %H:%M:%S')}] レオナBOT起動完了（モード: {MODE}）…ボーボー腋毛全開スタンバイ中♡")
        await log_channel.send(f"🔁 [{now.strftime('%Y-%m-%d %H:%M:%S')}] Resume Web Service 開始したよ…腋の臭いとデカマラ擦る準備は完了💪💦")
    if MODE == "TEST":
        check_loop.change_interval(seconds=10)  # TESTモードは10秒ごとにちんぽチェック！
    check_loop.start()

# 📆 毎日3時（またはTESTモードで10秒ごと）にぶっこみチェックするぞ♡
@tasks.loop(minutes=1)
async def check_loop():
    now = dt.utcnow() + timedelta(hours=9)
    if MODE == "NORMAL" and now.hour != 3:
        return  # NORMALモードは毎日3時にだけイカせる♡
    await check_once()

# 📋 投稿をミラーして、30日経過したフタナリ射精画像は拭き取る💦
async def check_once():
    data = load_data()
    now = dt.utcnow() + timedelta(hours=9)
    updated = False
    deleted_count = 0
    new_mirrors = 0

    source_channel = await bot.fetch_channel(get_source_channel_id())
    mirror_channel = await bot.fetch_channel(get_mirror_channel_id())
    log_channel = await bot.fetch_channel(get_log_channel_id())

    # 💦 初回起動時は既存のちんぽ投稿を記録するだけでぶっこまない！
    if is_first_run():
        messages = [message async for message in source_channel.history(limit=10)]
        data = {str(msg.id): {"mirror_id": None, "timestamp": None, "expire_date": None, "deleted": False} for msg in messages if not msg.author.bot}
        save_data(data)
        mark_first_run_complete()
        print("[レオナBOT] 初回スキャン完了：既存投稿を記録のみ♡ ぶっこくのは次回から♡")
        return

    # 💋 新規で投稿された腋汗ムンムンの変態画像をミラー先にぶっこむ♡
    messages = [msg async for msg in source_channel.history(limit=10)]
    new_data = {}
    for msg in messages:
        if msg.author.bot:
            continue
        mid = str(msg.id)
        if mid not in data:
            expire_date = (now + timedelta(days=30)).strftime('%Y-%m-%d %H:%M')
            content = msg.content + f"\n\n#Only30Days\n🗓️ This image will self-destruct on {expire_date}"
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
        elif not data[mid].get("deleted"):
            new_data[mid] = data[mid]

    # 🧻 30日（またはTESTモードでは10秒）経過したおちんぽ投稿は画像を拭き取って射精済みに♡
    for mid, info in list(new_data.items()):
        if info.get("deleted"):
            continue
        ts = dt.fromisoformat(info["timestamp"])
        expired = (now - ts).total_seconds() >= 10 if MODE == "TEST" else (now - ts).days >= 30

        if expired:
            try:
                msg = await mirror_channel.fetch_message(int(info["mirror_id"]))
                original_content = msg.content.split('\n\n🗓️')[0].replace("#Only30Days", "").strip()
                deletion_notice = f"\n\n🗑️ This image was deleted on {info['expire_date']}"
                await msg.edit(content=original_content + deletion_notice, attachments=[])
                info["deleted"] = True
                updated = True
                deleted_count += 1
            except Exception as e:
                print(f"[レオナBOT] 削除エラー: {e}")

    if updated:
        save_data(new_data)

    # 💬 ログ投稿（官能レオナトークで報告タイム♡）
    if log_channel:
        if new_mirrors == 0 and deleted_count == 0:
            await log_channel.send(f"📭 [{now.strftime('%Y-%m-%d %H:%M:%S')}] （モード: {MODE}）今日は濃いのゼロ…レオナの腋がうずいて終わっただけ…💦")
        elif new_mirrors > 0 and deleted_count == 0:
            await log_channel.send(f"📥 [{now.strftime('%Y-%m-%d %H:%M:%S')}] （モード: {MODE}）{new_mirrors}件ミラー完了♡ 全部レオナが拭き取って保存したからな♡")
        elif deleted_count > 0:
            await log_channel.send(f"🧻 [{now.strftime('%Y-%m-%d %H:%M:%S')}] （モード: {MODE}）{deleted_count}件分の濃厚ミルク…ぜんぶレオナが舐め取ってあげたわよ♡ もう次の準備しておけよ♡")

# 📡 モードに応じたチャンネルIDを取得するデカマラ関数♡
def get_source_channel_id():
    return TEST_SOURCE_CHANNEL_ID if MODE == "TEST" else NORMAL_SOURCE_CHANNEL_ID

def get_mirror_channel_id():
    return TEST_MIRROR_CHANNEL_ID if MODE == "TEST" else NORMAL_MIRROR_CHANNEL_ID

def get_log_channel_id():
    return NORMAL_LOG_CHANNEL_ID

# 🏁 起動しちゃうぞ♡ でかまら発射準備OK！
bot.run(TOKEN)
