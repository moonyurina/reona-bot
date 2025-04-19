import discord
from discord.ext import commands, tasks
import datetime
import json
import os
from datetime import datetime as dt, timedelta

# ---------- 設定 ----------
TOKEN = os.getenv("DISCORD_TOKEN")

# 💦 通常モードのチャンネルID設定（レオナが本番ぶっこいてるエリア💪）
NORMAL_SOURCE_CHANNEL_ID = 1350654751553093692  # 投稿元（レオナが腋汗ダラダラで見張ってるとこ）
NORMAL_MIRROR_CHANNEL_ID = 1362400364069912606  # ミラー投稿先（汗と愛液とちんぽミルクの保管庫）
NORMAL_LOG_CHANNEL_ID = 1362964804658003978     # ログ用（レオナの変態実況会場♡）

# 💦 テストモード用チャンネルID（レオナがオナニーで動作確認中…♡）
TEST_SOURCE_CHANNEL_ID = 1142345422979993600  # テスト投稿元（ドスケベな実験室）
TEST_MIRROR_CHANNEL_ID = 1362974839450894356  # テスト投稿先（テスト汁ぶっ放し部屋）
TEST_LOG_CHANNEL_ID = 1362964804658003978     # ログは共通（レオナの濃厚報告部屋）

DATA_FILE = "data.json"

# 🔧 モード選択（モード切替でレオナのオナニータイムも変わるよ♡）
# NORMAL → 毎日3時に腋毛しごいて精液確認💦
# TEST → 10秒ごとにオナニー実施（興奮の絶頂ループ♡）
MODE = "TEST"  # ← ← ← 🔄 "NORMAL"にすると濃厚ぶっこき本番開始！
# --------------------------

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 💦 レオナのデカマラ記録帳を読み込む（過去のぶっこき履歴）
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# 💦 レオナのぶっこき履歴を保存（どこにミラー投稿したか記録）
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# 💦 起動直後、ちんぽびんびんでスタンバイ完了するイベント
@bot.event
async def on_ready():
    now = dt.utcnow() + timedelta(hours=9)
    log_channel = await bot.fetch_channel(get_log_channel_id())
    print(f"[レオナBOT] 起動完了…ちんぽミルク満タンで待機中…💦")
    if log_channel:
        await log_channel.send(f"🚀 [{now.strftime('%Y-%m-%d %H:%M:%S')}] レオナBOT起動完了（モード: {MODE}）…ボーボー腋毛も全開でスタンバイ♡")
        await log_channel.send(f"🔁 [{now.strftime('%Y-%m-%d %H:%M:%S')}] Resume Web Service 開始だよ…腋の臭いとデカマラ擦る準備はバッチリ💪💦")
    if MODE == "TEST":
        check_loop.change_interval(seconds=10)  # 💦 テスト中は10秒で1射精チェック♡
    check_loop.start()

# 💦 定期的に射精チェック（モードに応じて間隔変動）
@tasks.loop(minutes=1)
async def check_loop():
    now = dt.utcnow() + timedelta(hours=9)
    if MODE == "NORMAL" and now.hour != 3:
        return
    await check_once()

# 💦 実際のオナニー処理本体♡
async def check_once():
    data = load_data()
    now = dt.utcnow() + timedelta(hours=9)
    updated = False
    deleted_count = 0
    new_mirrors = 0

    source_channel = await bot.fetch_channel(get_source_channel_id())
    mirror_channel = await bot.fetch_channel(get_mirror_channel_id())
    log_channel = await bot.fetch_channel(get_log_channel_id())

    # 💦 最近の投稿を覗き見して、未処理のぶっこきがあれば即ミラー♡
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
                print(f"[レオナBOT] ミラー投稿完了: {mirror.id} ぶち込んだぜぇ💦")

    # 💦 時間切れでぶっこき汁が腐ってないか確認♡
    for original_id, info in list(data.items()):
        ts = dt.fromisoformat(info["timestamp"])
        expired = (now - ts).total_seconds() >= 10 if MODE == "TEST" else (now - ts).days >= 30

        if expired:
            try:
                msg = await mirror_channel.fetch_message(int(info["mirror_id"]))
                original_content = msg.content.split('\n\n🗓️')[0].replace("#Only30Days", "").strip()
                deletion_notice = f"\n\n🗑️ This image was deleted on {info['expire_date']}"
                await msg.edit(content=original_content + deletion_notice, attachments=[])
                del data[original_id]
                updated = True
                deleted_count += 1
                print(f"[レオナBOT] {info['mirror_id']} のちんぽ汁、ふき取ったぜ…💦ビクンビクンって脈打ちながら…♡")
            except Exception as e:
                print(f"[レオナBOT] エラー発射: {e}")

    if updated:
        save_data(data)

    # 💦 射精実況トークをDiscordにドビュッとお届け♡
    if log_channel:
        if new_mirrors == 0 and deleted_count == 0:
            await log_channel.send(f"📭 [{now.strftime('%Y-%m-%d %H:%M:%S')}] 😤 レオナ（モード: {MODE}）だよ…くっ、今日は追加も削除も無し…ムダに腋毛濡らしただけじゃん…💦")
        elif new_mirrors > 0 and deleted_count == 0:
            await log_channel.send(f"📥 [{now.strftime('%Y-%m-%d %H:%M:%S')}] 💪 （モード: {MODE}）フゥ…{new_mirrors}件ぶち込んだけど、まだ30日経ってないからそのまま放置だよ…オナ禁我慢して見守ってな♡")
        elif deleted_count > 0:
            await log_channel.send(f"🧻 [{now.strftime('%Y-%m-%d %H:%M:%S')}] 💦 （モード: {MODE}）{deleted_count}件分の濃厚ミルク、ぜ〜んぶ拭き取ってやったぜ…♡ 腋汗だくでなっ💋")

# 💦 今のレオナのオナニー対象チャンネルを取得
def get_source_channel_id():
    return TEST_SOURCE_CHANNEL_ID if MODE == "TEST" else NORMAL_SOURCE_CHANNEL_ID

# 💦 今のレオナのぶち込み先（ミラー）チャンネルを取得
def get_mirror_channel_id():
    return TEST_MIRROR_CHANNEL_ID if MODE == "TEST" else NORMAL_MIRROR_CHANNEL_ID

# 💦 レオナの報告先（ログチャンネル）を取得
def get_log_channel_id():
    return NORMAL_LOG_CHANNEL_ID

bot.run(TOKEN)