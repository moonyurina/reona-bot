# 💦 ここはレオナの変態中柱♡ BOT起動の全コードよ♡

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
if not TOKEN:
    print("[レオナBOT] ❌ DISCORD_TOKEN が設定されてないよ！")
    exit(1)

# 🔥 本番チャンネル設定（濃厚ミラー♡）
NORMAL_SOURCE_CHANNEL_ID = 1350654751553093692
NORMAL_MIRROR_CHANNEL_ID = 1362400364069912606

# 💦 テストチャンネル設定（実験プレイ♡）
TEST_SOURCE_CHANNEL_ID = 1142345422979993600
TEST_MIRROR_CHANNEL_ID = 1362974839450894356

# 📬 ログチャンネル（実況報告♡）
LOG_CHANNEL_ID = 1362964804658003978

# 💋 モード切換スイッチ（本番かテストか…どっちでイく？）
MODE = "NORMAL"
DATA_FILE = "data_test.json" if MODE == "TEST" else "data.json"

# ⛏️ グローバル変数（起動時間とかログの管理♡）
startup_time = None
keep_alive_message = None
last_keep_alive_plain = None

# 📱 ディスコードの淫乱設定♡
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix=os.getenv("BOT_PREFIX", "!"), intents=intents)

# 🌐 Flaskたんでお外にお知らせ♡
app = Flask(__name__)

@app.route('/')
def home():
    summary = get_summary_text()
    return f"レオナBOT生きてるよ♡\n{summary}シコリ目だお"

# 🚀 Flaskちゃんを並列で立ち上げる♡
def run_flask():
    app.run(host="0.0.0.0", port=8080)

# 📂 保存データの読み込み♡
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[レオナBOT] ⚠️ dataファイル読めなかったよ…壊れてるかも♡ 初期化するね♡ → {e}")
            return {}
    return {}

# 📂 保存時に30日超えの古い子は削除しちゃう♡
def save_data(data):
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

# ⏰ ミラー作業するべき時間帯かチェック♡（夜中だけ変態稽働♡）
def is_mirror_check_time():
    now = dt.utcnow() + timedelta(hours=9)
    return 0 <= now.hour < 4

# 🌍 RailwayかRenderか、起動元を確認♡
def get_deploy_source():
    return socket.gethostname()

# ⏱️ レオナの精疲時間を計算♡（起動時間から今まで♡）
def get_uptime():
    if not startup_time:
        return "（起動時間不明…レオナまだイってない♡）"
    now = dt.utcnow()
    delta = now - startup_time
    hours, remainder = divmod(delta.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"💡 精疲時間: {int(hours)}時間 {int(minutes)}分 {int(seconds)}秒"

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

# 💥 Flaskでも表示したい要総♡
def get_summary_text():
    data = load_data()
    total = len(data)
    deleted = sum(1 for d in data.values() if d.get("deleted"))
    return f"📊 {total}件中 {deleted}件が削除されたよ♡ "

# 🔍 !checkコマンド♡（詳細チェック♡）
@bot.command()
async def check(ctx):
    data = load_data()
    recent_items = sorted(data.items(), key=lambda x: x[1].get("timestamp", ""), reverse=True)[:10]
    lines = ["🔍 最新10件のミラー元メッセージの削除チェックを始めるよ♡"]
    deleted_count = 0
    for mid, info in recent_items:
        ts = info.get("timestamp")
        deleted = info.get("deleted", False)
        status = "🗑️ 削除済み" if deleted else "✅ 存在"
        ts_display = dt.fromisoformat(ts).strftime("%Y-%m-%d") if ts else "?"
        lines.append(f"・{mid} ({ts_display}) → {status}")
        if deleted:
            deleted_count += 1

    if deleted_count == 0:
        lines.append("👌 削除されたメッセージはなかったみたい♡")
    lines.append(get_mirror_status())
    lines.append(get_uptime())
    lines.append(f"🚉 起動元: `{get_deploy_source()}`")
    lines.append(get_command_info())

    await ctx.send("\n".join(lines))

# ✅ 定期ログ更新ループ（変化ないなら前消して更新♡）
@tasks.loop(minutes=10)
async def keep_alive_loop():
    global keep_alive_message, last_keep_alive_plain
    log_channel = await bot.fetch_channel(LOG_CHANNEL_ID)
    summary = get_summary_text()
    now = dt.utcnow() + timedelta(hours=9)
    new_msg = f"💓 {now.strftime('%Y-%m-%d %H:%M:%S')} レオナBOTまだ生きてるよ♡\n{summary}シコリ目だお"

    if keep_alive_message and keep_alive_message.channel.id == log_channel.id:
        if new_msg == last_keep_alive_plain:
            try:
                await keep_alive_message.delete()
                keep_alive_message = await log_channel.send(new_msg)
                last_keep_alive_plain = new_msg
            except Exception as e:
                print(f"[レオナBOT] keep_aliveループでメッセージ削除失敗: {e}")
        else:
            keep_alive_message = await log_channel.send(new_msg)
            last_keep_alive_plain = new_msg
    else:
        keep_alive_message = await log_channel.send(new_msg)
        last_keep_alive_plain = new_msg

# ▶️ 起動ログとともにDiscordボットを起動♡
if __name__ == "__main__":
    startup_time = dt.utcnow()
    print(f"[レオナBOT] 🚀 起動するよ♡ 起動元: {get_deploy_source()}")

    threading.Thread(target=run_flask, daemon=True).start()

    @bot.event
    async def on_ready():
        print(f"[レオナBOT] ✅ Discordにログイン完了！ {bot.user}")
        keep_alive_loop.start()

    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"[レオナBOT] ❌ Discordログイン失敗かも！？ → {e}")
