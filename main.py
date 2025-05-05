

import discord
from discord.ext import commands, tasks
import datetime
import json
import os
from datetime import datetime as dt, timedelta
from flask import Flask
import threading
import asyncio
import socket

# 💋 セクシーなトークンちゃんを.envからお迎え♡
TOKEN = os.getenv("DISCORD_TOKEN")

# 🔥 本番チャンネル設定（濃厚ミラー♡）
NORMAL_SOURCE_CHANNEL_ID = 1350654751553093692
NORMAL_MIRROR_CHANNEL_ID = 1362400364069912606

# 💦 テストチャンネル設定（実験プレイ♡）
TEST_SOURCE_CHANNEL_ID = 1142345422979993600
TEST_MIRROR_CHANNEL_ID = 1362974839450894356

# 📢 ログチャンネル（実況報告♡）
LOG_CHANNEL_ID = 1362964804658003978

# 💋 モード切替スイッチ（本番かテストか…どっちでイく？）
MODE = "NORMAL"
DATA_FILE = "data_test.json" if MODE == "TEST" else "data.json"

# 🔧 グローバル変数（起動時間とかログの管理♡）
startup_time = None
keep_alive_message = None
last_keep_alive_plain = None

# 📡 ディスコードの淫乱設定♡
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix=os.getenv("BOT_PREFIX", "!"), intents=intents)

# 🌐 Flaskたんでお外にお知らせ♡
app = Flask(__name__)

@app.route('/')
def home():
    return "レオナBOT生きてるよ♡"

# 🚀 Flaskちゃんを並列で立ち上げる♡
def run_flask():
    app.run(host="0.0.0.0", port=8080)

# 📂 保存データの読み込み♡
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("[レオナBOT] ⚠️ dataファイルが壊れてるみたい…初期化するよ♡")
            return {}
    return {}

# 💾 保存時に30日超えの古い子は削除しちゃう♡
def save_data(data):
    # 💿 データ変更がなければ無駄にイかない♡ キャッシュでおさえる♡
    old_data = load_data()
    if json.dumps(data, sort_keys=True) == json.dumps(old_data, sort_keys=True):
        return
    now = dt.utcnow()
    before = len(data)
    filtered_data = {
        mid: info for mid, info in data.items()
        if (dt.fromisoformat(info.get("timestamp", now.isoformat())) + timedelta(days=30)) > now
    }
    after = len(filtered_data)
    removed = before - after
    if removed > 0:
        print(f"[レオナBOT] 💣 {removed} 件の古いミラーデータを削除したよ♡（30日超え）")
    with open(DATA_FILE, "w") as f:
        json.dump(filtered_data, f)

# 🕒 現在のUTC時刻をゲット♡
def get_now_utc():
    return dt.utcnow()

# ⏰ ミラー作業するべき時間帯かチェック♡（夜中だけ変態稼働♡）
def is_mirror_check_time():
    now = dt.utcnow() + timedelta(hours=9)
    return 0 <= now.hour < 4

# 🌍 RailwayかRenderか、起動元を確認♡
def get_deploy_source():
    return socket.gethostname()

# 📜 使えるコマンドたちを紹介するよ♡
def get_command_info():
    return (
        "📝 コマンド一覧\n"
        "`!mirror <message_id>` → 指定IDのメッセージをミラーするよ♡\n"
        "`!check` → 最新10件の削除チェックをするよ♡\n"
    )

# 📊 現在のミラー状況（何件保存されてるか♡）
def get_mirror_status():
    data = load_data()
    total = len(data)
    deleted = sum(1 for d in data.values() if d.get("deleted"))
    return f"📊 ミラー総数: {total}件 / 削除済み: {deleted}件"

# 💓 レオナBOTが10分ごとにオナ声あげるやつ♡（生きてる確認）
@tasks.loop(minutes=10)
async def keep_alive_loop():
    global keep_alive_message, last_keep_alive_plain
    log_channel = await bot.fetch_channel(LOG_CHANNEL_ID)
    now = dt.utcnow() + timedelta(hours=9)
    try:
        header = (
            f"🕘 {now.strftime('%Y-%m-%d %H:%M:%S')} 現在のレオナBOT状況だお♡\n"
            f"💻 reonaBOTは `{get_deploy_source()}` 経由でシコシコしてるお♡\n"
        )
        plain_log = (
            get_mirror_status() + "\n" +
            get_command_info()
        )
        new_msg = header + plain_log

        # 同じ内容だったら前のログを削除して、新しくイかせる♡
        if keep_alive_message and keep_alive_message.channel.id == log_channel.id:
            if plain_log == last_keep_alive_plain:
                await keep_alive_message.delete()
            keep_alive_message = await log_channel.send(new_msg)
        else:
            keep_alive_message = await log_channel.send(new_msg)

        last_keep_alive_plain = plain_log

    except Exception as e:
        print(f"[レオナBOT] keep_alive_loop エラー: {e}")

# 🧼 !checkコマンドで最新10件を検査♡（削除されてたらミラーも消す♡）
@bot.command(name="check")
async def manual_check_deleted_messages(ctx):
    await ctx.send("🔍 最新10件のミラー元メッセージの削除チェックを始めるよ♡")
    data = load_data()
    updated = 0
    checked_list = []

    source_channel = await bot.fetch_channel(NORMAL_SOURCE_CHANNEL_ID if MODE == "NORMAL" else TEST_SOURCE_CHANNEL_ID)
    mirror_channel = await bot.fetch_channel(NORMAL_MIRROR_CHANNEL_ID if MODE == "NORMAL" else TEST_MIRROR_CHANNEL_ID)
    log_channel = await bot.fetch_channel(LOG_CHANNEL_ID)

    for mid, info in list(data.items())[-10:]:
        status = "✅ 存在"
        if info.get("deleted"):
            continue

        try:
            await source_channel.fetch_message(int(mid))
        except discord.NotFound:
            try:
                mirror_msg = await mirror_channel.fetch_message(info["mirror_id"])
                await mirror_msg.delete()
            except Exception as e:
                print(f"[レオナBOT] ミラーメッセージ削除エラー: {e}")

            info["deleted"] = True
            updated += 1
            status = "❌ 削除"
            if log_channel:
                await log_channel.send(f"❌ 元メッセージが削除されたので、ミラーも削除したよ → ID: {mid}")

        timestamp = info.get("timestamp", "N/A")
        expire = info.get("expire_date", "N/A")
        checked_list.append(f"ID: {mid} → {status}｜📅 投稿: {timestamp}｜⌛ 削除予定: {expire}")
        await asyncio.sleep(0.5)

    if updated > 0:
        save_data(data)
    status_report = "\n".join(checked_list)
    await ctx.send(f"🧾 チェック結果一覧：\n{status_report}")
    if updated > 0:
        await ctx.send(file=discord.File("assets/delete_success.gif"))
    else:
        await ctx.send(file=discord.File("assets/nothing_deleted.gif"))
