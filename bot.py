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

    link = f"https://www.youtube.com/watch?v={video_id}"
    thumbnail = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

    return link, thumbnail


def send_to_telegram(link, thumbnail):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"

    data = {
        "chat_id": TELEGRAM_CHANNEL,
        "photo": thumbnail,
        "caption": link
    }

    response = requests.post(url, data=data, timeout=60)
    response.raise_for_status()

    result = response.json()

    if not result.get("ok"):
        raise RuntimeError(f"Telegram API error: {result}")


def main():
    video = get_latest_video()

    if not video:
        print("No video found.")
        return

    link, thumbnail = video
    previous_video = ""

    if os.path.exists(LAST_VIDEO_FILE):
        with open(LAST_VIDEO_FILE, "r", encoding="utf-8") as file:
            previous_video = file.read().strip()

    if link == previous_video:
        print("Video already posted.")
        return

    send_to_telegram(link, thumbnail)

    with open(LAST_VIDEO_FILE, "w", encoding="utf-8") as file:
        file.write(link)

    print(f"Posted video and thumbnail: {link}")


if __name__ == "__main__":
    main()
