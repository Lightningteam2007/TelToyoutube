from bs4 import BeautifulSoup

class ContentAnalyzer:
    BASE_URL = "https://t.me"

    @staticmethod
    def analyze(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        messages = []

        for message in soup.find_all('div', class_='tgme_widget_message'):
            time_tag = message.find('time', class_='time')
            message_time = time_tag['datetime'] if time_tag else None
            msg_id = message.get('data-post', '').split('/')[-1]

            video_div = message.find('div', class_='tgme_widget_message_video_wrap')
            if video_div:
                video_url = video_div.find('video')['src']
                if not video_url.startswith("http"):
                    video_url = ContentAnalyzer.BASE_URL + video_url
                messages.append({'type': 'video', 'url': video_url, 'time': message_time, 'id': msg_id})
                continue

            photo_div = message.find('a', class_='tgme_widget_message_photo_wrap')
            if photo_div:
                style = photo_div.get('style', '')
                image_url = style.split('url(')[1].split(')')[0]
                if not image_url.startswith("http"):
                    image_url = ContentAnalyzer.BASE_URL + image_url
                messages.append({'type': 'image', 'url': image_url, 'time': message_time, 'id': msg_id})
                continue

            messages.append({'type': 'text', 'content': message.get_text(), 'time': message_time, 'id': msg_id})

        return messages
