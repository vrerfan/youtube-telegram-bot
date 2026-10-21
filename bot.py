import os
import re
import requests

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
API = f"https://api.telegram.org/bot{TOKEN}"


def get_video_id(text):
    patterns = [
        r"(?:youtube\.com/watch\?.*?v=)([A-Za-z0-9_-]{11})",
        r"youtu\.be/([A-Za-z0-9_-]{11})",
        r"youtube\.com/shorts/([A-Za-z0-9_-]{11})",
        r"youtube\.com/embed/([A-Za-z0-9_-]{11})",
        r"youtube\.com/live/([A-Za-z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return match.group(1)

    return None


def send_thumbnail(chat_id, video_id):
    thumbnails = [
        f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
        f"https://i.ytimg.com/vi/{video_id}/sddefault.jpg",
        f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
        f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg",
    ]

    for thumbnail_url in thumbnails:
        try:
            response = requests.get(thumbnail_url, timeout=20)
            response.raise_for_status()

            if len(response.content) < 5000:
                continue

            result = requests.post(
                f"{API}/sendDocument",
                data={"chat_id": chat_id},
                files={
                    "document": (
                        f"{video_id}_thumbnail.jpg",
                        response.content,
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

    requests.post(
        f"{API}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": "متأسفانه تامنیل این ویدیو دریافت نشد."
        },
        timeout=30
    )


def main():
    offset = None

    while True:
        try:
            response = requests.get(
                f"{API}/getUpdates",
                params={"offset": offset, "timeout": 30},
                timeout=40
            )
            response.raise_for_status()

            for update in response.json().get("result", []):
                offset = update["update_id"] + 1

                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                text = message.get("text", "")

                if not chat_id or not text:
                    continue

                if text.startswith("/start"):
                    requests.post(
                        f"{API}/sendMessage",
                        data={
                            "chat_id": chat_id,
                            "text": "لینک ویدیوی یوتیوب رو بفرست تا تامنیلش رو به‌صورت فایل عکس برات بفرستم."
                        },
                        timeout=30
                    )
                    continue

                video_id = get_video_id(text)

                if video_id:
                    send_thumbnail(chat_id, video_id)
                else:
                    requests.post(
                        f"{API}/sendMessage",
                        data={
                            "chat_id": chat_id,
                            "text": "لطفاً لینک معتبر یوتیوب بفرست."
                        },
                        timeout=30
                    )

        except requests.RequestException as error:
            print(error)


if __name__ == "__main__":
    main()
