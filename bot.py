import telebot
import requests
import time

TELEGRAM_TOKEN = os.environ.get("8940879483:AAGXIR21CZLHvTKINzWXy1Zj2iOpsrpR6b0", "")
YU28_API_KEY = os.environ.get("yu28_d15c4d8f4e54d77d", "")
CHAT_ID = os.environ.get("-1003919784583", "")
CHECK_INTERVAL = 200 
# ==========================================

bot = telebot.TeleBot(TELEGRAM_TOKEN)
last_issue = ""

def get_kj_data(nbr=1):
    url = f"https://yu28.top/api/kj?nbr={nbr}"
    headers = {"X-Api-Key": YU28_API_KEY, "Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            data_list = data.get('data', data) if isinstance(data, dict) else data
            if isinstance(data_list, list) and len(data_list) > 0:
                return data_list[0]
    except Exception as e:
        print(f"请求接口失败: {e}")
    return None

def auto_broadcast():
    global last_issue
    print("⏳ 自动播报任务已启动...")
    while True:
        item = get_kj_data(1)
        if item:
            qh = item.get('qh') or item.get('issue') or item.get('period')
            nbr = item.get('nbr') or item.get('number') or item.get('code')
            time_str = item.get('time') or item.get('date') or item.get('openTime')
            if qh and qh != last_issue:
                last_issue = qh
                msg = f"🔔 **新开奖啦！**\n\n期号: `{qh}`\n号码: **{nbr}**\n时间: {time_str}"
                try:
                    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
                except Exception as e:
                    print(f"播报失败，请检查CHAT_ID: {e}")
        time.sleep(CHECK_INTERVAL)

@bot.message_handler(commands=['kj'])
def manual_query(message):
    nbr = message.text.split()[1] if len(message.text.split()) > 1 else "5"
    item_list = get_kj_data(int(nbr))
    if not item_list:
        bot.reply_to(message, "❌ 获取数据失败")
        return
    reply = f"📊 最近 {nbr} 期数据：\n\n"
    for item in item_list:
        qh = item.get('qh') or item.get('issue') or "未知"
        num = item.get('nbr') or item.get('number') or "未知"
        reply += f"期号: `{qh}` | 号码: **{num}**\n"
    bot.reply_to(message, reply, parse_mode='Markdown')

if __name__ == "__main__":
    t = threading.Thread(target=auto_broadcast, daemon=True)
    t.start()
    bot.infinity_polling()