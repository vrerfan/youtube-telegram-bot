import os
import requests
import xml.etree.ElementTree as ET

CHANNEL_ID = "UC3YkcqEaQQKjYmGdZ0gDnAg"
TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHANNEL = "@Zenoxer_yt"

FEED_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
LAST_VIDEO_FILE = "last_video.txt"


def get_latest_video():
    response = requests.get(FEED_URL, timeout=30)
    response.raise_for_status()

    root = ET.fromstring(response.content)

    ns = {
        "yt": "http://www.youtube.com/xml/schemas/2015",
        "atom": "http://www.w3.org/2005/Atom"
    }

    entry = root.find("atom:entry", ns)

    if entry is None:
        return None

    video_id = entry.findtext("yt:videoId", namespaces=ns)

    if not video_id:
        return None

    return f"https://www.youtube.com/watch?v={video_id}"


def send_to_telegram(link):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data = {
        "chat_id": TELEGRAM_CHANNEL,
        "text": link,
        "link_preview_options": (
            '{"is_disabled": false, "prefer_large_media": true}'
        )
    }

    response = requests.post(url, data=data, timeout=30)
    response.raise_for_status()

    result = response.json()

    if not result.get("ok"):
        raise RuntimeError(f"Telegram API error: {result}")


def main():
    latest_video = get_latest_video()

    if not latest_video:
        print("No video found.")
        return

    previous_video = ""

    if os.path.exists(LAST_VIDEO_FILE):
        with open(LAST_VIDEO_FILE, "r", encoding="utf-8") as file:
            previous_video = file.read().strip()

    if latest_video == previous_video:
        print("Video already posted.")
        return

    send_to_telegram(latest_video)

    with open(LAST_VIDEO_FILE, "w", encoding="utf-8") as file:
        file.write(latest_video)

    print(f"Posted successfully: {latest_video}")


if __name__ == "__main__":
    main()
