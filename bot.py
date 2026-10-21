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
    ns = {"yt": "http://www.youtube.com/xml/schemas/2015",
          "atom": "http://www.w3.org/2005/Atom"}

    entry = root.find("atom:entry", ns)
    if entry is None:
        return None

    video_id = entry.findtext("yt:videoId", namespaces=ns)
    return f"https://www.youtube.com/watch?v={video_id}"

def send_to_telegram(link):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    response = requests.post(
        url,
        data={"chat_id": TELEGRAM_CHANNEL, "text": link},
        timeout=30
    )
    response.raise_for_status()

def main():
    latest_video = get_latest_video()
    if not latest_video:
        return

    previous_video = ""
    if os.path.exists(LAST_VIDEO_FILE):
        with open(LAST_VIDEO_FILE, "r") as f:
            previous_video = f.read().strip()

    if latest_video != previous_video:
        send_to_telegram(latest_video)
        with open(LAST_VIDEO_FILE, "w") as f:
            f.write(latest_video)

if __name__ == "__main__":
    main()
