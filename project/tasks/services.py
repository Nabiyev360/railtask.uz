import requests as req
from UzTransliterator import UzTransliterator

trans = UzTransliterator.UzTransliterator()

def to_latin(txt):
    latin_text = trans.transliterate(text=txt, from_="cyr", to="lat")
    return latin_text


bot_token = '8013793190:AAFmUBLpgT6MYXfwLzgVA1p0TxXxpKOgui4'
BASE_URL = f'https://api.telegram.org/bot{bot_token}/sendMessage'


def send_telegram_message(chat_id, text, parse_mode=None):
    if not chat_id:
        return
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    if parse_mode:
        payload['parse_mode'] = parse_mode

    try:
        res = req.get(BASE_URL, params=payload, timeout=5)
        if res.status_code != 200:
            print(f"⚠️ Xatolik yuborishda (chat_id={chat_id}): {res.text}")
    except Exception as e:
        print(f"❌ Ulanishda xatolik (chat_id={chat_id}): {e}")


def send_task_tg_users(task):
    message = (
        f"🔰 #topshiriq №{task.id}\n\n"
        f"⚜️ {task.author.full_name}\n\n"
        f"🧾 {task.title}\n\n"
        f"📃 {task.description}\n\n"
        f"📆 {task.deadline.strftime('%d.%m.%Y %H:%M')}\n\n"
    )
    for chat_id in task.performers.values_list('tg_id', flat=True):
        send_telegram_message(chat_id, message)


def tg_send_answer_assigner(task, performer, text):
    message = (
        f"🔰 #topshiriq №{task.id}\n\n"
        f"👨‍💼 Javob berdi: {performer}\n\n"
        f"🧾 {text}\n\n"
    )
    send_telegram_message(task.author.tg_id, message)


def tg_send_file_assigner(task, performer, file):
    message = (
        f"🔰 #topshiriq №{task.id}\n\n"
        f"👨‍💼 Javob berdi: {performer}\n\n"
        f"🧾 <a href='https://railtask.uz/{file}'>{file.name[19:]}</a>\n\n"
    )
    send_telegram_message(task.author.tg_id, message, parse_mode='HTML')



