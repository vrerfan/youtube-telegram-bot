import os
import re
import time
import requests

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

API = f"https://api.telegram.org/bot{TOKEN}"
session = requests.Session()


def get_video_id(link):
    patterns = [
        r"(?:youtube\.com/watch\?.*?v=)([A-Za-z0-9_-]{11})",
        r"youtu\.be/([A-Za-z0-9_-]{11})",
        r"youtube\.com/shorts/([A-Za-z0-9_-]{11})",
        r"youtube\.com/embed/([A-Za-z0-9_-]{11})",
        r"youtube\.com/live/([A-Za-z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, link)

        if match:
            return match.group(1)

    return None


def send_message(chat_id, text):
    session.post(
        f"{API}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": text
        },
        timeout=30
    )


def send_thumbnail(chat_id, video_id):
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    thumbnails = [
        f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
        f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    ]

    for thumbnail in thumbnails:
        try:
            image_response = requests.get(
                thumbnail,
                timeout=20
            )
            image_response.raise_for_status()

            if len(image_response.content) < 1000:
                continue

            result = session.post(
                f"{API}/sendPhoto",
                data={
                    "chat_id": chat_id,
                    "caption": video_url
                },
                files={
                    "photo": (
                        "thumbnail.jpg",
                        image_response.content,
                        "image/jpeg"
                    )
                },
                timeout=60
            )

            data = result.json()

            if data.get("ok"):
                return

        except requests.RequestException:
            continue

    send_message(
        chat_id,
        "دریافت تامنیل ناموفق بود. ممکن است ویدیو یا تصویر آن در دسترس نباشد."
    )


def main():
    session.post(
        f"{API}/deleteWebhook",
        timeout=30
    ).raise_for_status()

    offset = None

    print("YouTube Thumbnail Bot is running...")

    while True:
        try:
            response = session.get(
                f"{API}/getUpdates",
                params={
                    "offset": offset,
                    "timeout": 30,
                    "allowed_updates": '["message"]'
                },
                timeout=40
            )

            response.raise_for_status()
            updates = response.json()

            if not updates.get("ok"):
                time.sleep(3)
                continue

            for update in updates["result"]:
                offset = update["update_id"] + 1

                message = update.get("message", {})
                chat = message.get("chat", {})
                chat_id = chat.get("id")
                text = message.get("text", "")

                if not chat_id or not text:
                    continue

                if text.startswith("/start"):
                    send_message(
                        chat_id,
                        "سلام! لینک ویدیوی یوتیوب رو بفرست تا تامنیلش رو برات ارسال کنم."
                    )
                    continue

                video_id = get_video_id(text)

                if video_id:
                    send_thumbnail(chat_id, video_id)
                else:
                    send_message(
                        chat_id,
                        "لطفاً یک لینک معتبر از ویدیوی یوتیوب بفرست."
                    )

        except (requests.RequestException, ValueError) as error:
            print(f"Connection error: {error}")
            time.sleep(5)


if __name__ == "__main__":
    main()
