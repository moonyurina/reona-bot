        # 💦 ここはレオナの夏夏中柱♡ BOT起動の全コードよ♡

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
import time
import traceback

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
startup_time = dt.utcnow()
keep_alive_message = None
last_keep_alive_plain = None
log_history = []  # 📘 !log 用のログ履歴

# 📱 ディスコードの死体設定♡
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
    print("[レオナBOT] 🌐 Flaskサーバーを起動したよ♡")
    try:
        app.run(host="0.0.0.0", port=8080)
        except Exception as e:
        print(f"[レオナBOT] ❌ Flask起動中にエラーが発生したよ → {e}")
        traceback.print_exc()


# 📂 保存データの読み込み♡
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[レオナBOT] ⚠️ dataファイル読めなかったよ…壊れてるかも♡ 初期化するね♡ → {e}")
            traceback.print_exc()
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
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(filtered_data, f)
    except Exception as e:
        print(f"[レオナBOT] ❌ データ保存に失敗したよ！ → {e}")
        traceback.print_exc()

# 💫 コマンドサマリと状況まとめ関数♡
def get_summary_text():
    try:
        data = load_data()
        total = len(data)
        deleted = sum(1 for d in data.values() if d.get("deleted"))
        return f"📊 {total}件中 {deleted}件が削除されたよ♡ "
    except Exception as e:
        print(f"[レオナBOT] ❌ get_summary_textでエラー発生 → {e}")
        traceback.print_exc()
        return "（要約取得失敗…♡）"

def get_mirror_status():
    data = load_data()
    total = len(data)
    deleted = sum(1 for d in data.values() if d.get("deleted"))
    return f"📊 ミラー総数: {total}件 / 削除済み: {deleted}件"

@bot.command()
async def check(ctx):
            try:
                data = load_data()
                latest_ids = list(data.keys())[-10:]
                result_lines = ["🔍 最新10件のミラー元メッセージの削除チェックを始めるよ♡"]
                deleted_count = 0

                for mid in latest_ids:
                    item = data.get(mid, {})
                    ts = dt.fromisoformat(item.get("timestamp", dt.utcnow().isoformat())).strftime("%Y-%m-%d")
                    state = "✅ 存在"
                    try:
                        ch = await bot.fetch_channel(item["source_channel_id"])
                        await ch.fetch_message(int(mid))
                    except:
                        item["deleted"] = True
                        deleted_count += 1
                        state = "🗑️ 削除済み"
                    result_lines.append(f"・{mid} ({ts}) → {state}")

                save_data(data)
                result_lines.append("")
                result_lines.append(get_mirror_status())
                uptime = dt.utcnow() - startup_time
                hours, rem = divmod(uptime.total_seconds(), 3600)
                minutes, seconds = divmod(rem, 60)
                result_lines.append(f"💡 精疲時間: {int(hours)}時間 {int(minutes)}分 {int(seconds)}秒")
                result_lines.append(f"🚉 起動元: {socket.gethostname()}")
                result_lines.append("")
                result_lines.append("📝 コマンド一覧")
                result_lines.append("!mirror <message_id> → 指定IDのメッセージをミラーするよ♡")
                result_lines.append("!check → 最新10件の削除チェックをするよ♡")

                await ctx.send("\n".join(result_lines))
            except Exception as e:
                await ctx.send(f"❌ チェック中にエラーが出たよ！ → {e}")
                traceback.print_exc()



@bot.command()
async def check(ctx):
    try:
        data = load_data()
        latest_ids = list(data.keys())[-10:]
        deleted_count = 0
        for mid in latest_ids:
            item = data[mid]
            if item.get("deleted"):
                continue
            source_channel_id = item.get("source_channel_id")
            if not source_channel_id:
                print(f"[レオナBOT] ⚠️ データに source_channel_id がないからスキップするね → {mid}")
                continue
            try:
                ch = await bot.fetch_channel(source_channel_id)
                await ch.fetch_message(int(mid))
            except discord.NotFound:
                item["deleted"] = True
                deleted_count += 1
        save_data(data)

        summary = get_mirror_status()
        await ctx.send(f"🔍 最新10件のミラー元メッセージの削除チェックを始めるよ♡\n{summary}")
        if deleted_count:
            await ctx.send(f"⚠️ {deleted_count}件 削除されてたよ…♡")
        else:
            await ctx.send("👌 削除されたメッセージはなかったみたい♡")
    except Exception as e:
        await ctx.send(f"❌ チェック中にエラーが出たよ！ → {e}")
        traceback.print_exc()
@bot.command()
async def log(ctx):
    history = "\n".join(log_history[-5:]) or "（ログがまだないよ♡）"
    await ctx.send(f"📝 最新のログ履歴だよ♡\n{history}")

@bot.command()
async def stats(ctx):
    uptime = dt.utcnow() - startup_time
    hours, remainder = divmod(uptime.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    await ctx.send(f"📈 稼働時間: {int(hours)}時間 {int(minutes)}分 {int(seconds)}秒だよ♡\n{get_mirror_status()}")

@bot.event
async def on_disconnect():
    print("[レオナBOT] ⚠️ Discordから切断されたっぽいよ！")

@bot.event
async def on_resumed():
    print("[レオナBOT] ✅ Discordへの接続が再開されたよ！")

@bot.event
async def on_ready():
    print(f"[レオナBOT] 💖 ログイン成功！ → {bot.user}（ID: {bot.user.id}）")

    if not check_loop.is_running():
        check_loop.start()
        print("[レオナBOT] 🔁 check_loop スタートしたよ♡")
    if not keep_alive_loop.is_running():
        keep_alive_loop.start()
        print("[レオナBOT] 🔁 keep_alive_loop スタートしたよ♡")

@tasks.loop(minutes=10)
async def keep_alive_loop():
    global keep_alive_message, last_keep_alive_plain
    try:
        log_channel = await bot.fetch_channel(LOG_CHANNEL_ID)
        summary = get_summary_text()
        now = dt.utcnow() + timedelta(hours=9)
        new_msg = f"💓 {now.strftime('%Y-%m-%d %H:%M:%S')} レオナBOTまだ生きてるよ♡\n{summary}シコリ目だお"
        print(f"[レオナBOT] 🕒 keep_alive_loop → {new_msg}")

        log_history.append(new_msg)
        if len(log_history) > 20:
            log_history.pop(0)

        if keep_alive_message and keep_alive_message.channel.id == log_channel.id:
            await keep_alive_message.edit(content=new_msg)
            last_keep_alive_plain = new_msg
        else:
            keep_alive_message = await log_channel.send(new_msg)
            last_keep_alive_plain = new_msg
    except Exception as e:
        print(f"[レオナBOT] ❌ keep_alive_loop中にエラーが出たよ… → {e}")
        traceback.print_exc()

@tasks.loop(minutes=10)
async def check_loop():
    try:
        data = load_data()
        latest_ids = list(data.keys())[-10:]
        changed = False
        for mid in latest_ids:
            item = data[mid]
            if item.get("deleted"):
                continue
            try:
                ch = await bot.fetch_channel(item["source_channel_id"])
                await ch.fetch_message(int(mid))
            except discord.NotFound:
                item["deleted"] = True
                changed = True
        if changed:
            save_data(data)
    except Exception as e:
        print(f"[レオナBOT] ❌ check_loop中にエラーが出たよ！ → {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("[レオナBOT] 🔧 全体の初期化を始めるよ…♡")
    threading.Thread(target=run_flask).start()

    while True:
        try:
            print(f"[レオナBOT] 🚀 起動するよ♡ 起動元: {socket.gethostname()}")
            bot.run(TOKEN)
        except Exception as e:
            print(f"[レオナBOT] ❌ 致命的エラーで落ちたよ♡ 再起動まで1時間待つね… → {e}")
            traceback.print_exc()
            time.sleep(3600)
