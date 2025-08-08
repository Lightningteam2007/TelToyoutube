import os
import time
import logging
import random
import requests
from dotenv import load_dotenv
from content_analyzer import ContentAnalyzer
from state_manager import StateManager
from video_processor import process_video
from uploader import YouTubeUploader

load_dotenv()

TELEGRAM_CHANNEL = os.getenv("TELEGRAM_CHANNEL")
MAX_UPLOADS = int(os.getenv("MAX_UPLOADS_PER_DAY", 3))

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

session = requests.Session()
session.headers.update(HEADERS)

def setup_logging():
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/telegram_to_yt.log'),
            logging.StreamHandler()
        ]
    )

def fetch_telegram_content():
    try:
        response = session.get(TELEGRAM_CHANNEL, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.error(f"Error fetching Telegram content: {str(e)}")
        return None

def download_content(url, content_type):
    try:
        os.makedirs('temp', exist_ok=True)
        ext = 'mp4' if content_type == 'video' else 'jpg'
        filename = f"temp/{int(time.time())}.{ext}"

        with session.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return filename
    except Exception as e:
        logging.error(f"Error downloading {content_type}: {str(e)}")
        return None

def main():
    setup_logging()
    state = StateManager()
    uploader = YouTubeUploader()

    if not state.can_upload_more(MAX_UPLOADS):
        logging.info("Daily upload limit reached. Exiting.")
        return

    logging.info("Starting Telegram to YouTube upload process...")
    html_content = fetch_telegram_content()
    if not html_content:
        return

    analyzer = ContentAnalyzer()
    all_messages = analyzer.analyze(html_content)
    new_messages = state.get_new_messages(all_messages)

    if not new_messages:
        logging.info("No new messages found since last check.")
        return

    logging.info(f"Found {len(new_messages)} new messages to process")

    for message in reversed(new_messages):
        try:
            if message['type'] != 'video':
                logging.info(f"Skipping non-video message (ID: {message['id']})")
                state.state['last_processed_id'] = message['id']
                state.save_state()
                continue

            if not state.can_upload_more(MAX_UPLOADS):
                logging.info("Daily upload limit reached. Stopping.")
                break

            video_path = download_content(message['url'], 'video')
            if not video_path:
                continue

            processed_path = process_video(video_path)
            upload_result = uploader.upload_video(processed_path)

            if upload_result:
                state.update_upload_stats()
                state.state['last_processed_id'] = message['id']
                state.save_state()

            os.remove(video_path)
            os.remove(processed_path)
            time.sleep(random.randint(60, 120))

        except Exception as e:
            logging.error(f"Error processing message {message['id']}: {str(e)}")
            continue

    logging.info("Process completed successfully")

if __name__ == "__main__":
    main()
