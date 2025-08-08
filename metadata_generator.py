import random
from datetime import datetime

def generate_metadata():
    hashtags = [
        "#shorts", "#viral", "#trending", "#funny", 
        "#meme", "#comedy", "#telegram", "#fyp",
        "#ایران", "#طنز", "#خنده", "#میم"
    ]
    selected_tags = random.sample(hashtags, 5)
    title = f"ویدیوی طنز {datetime.now().strftime('%d/%m')} 🚀"
    description = "\n".join([
        "ویدیوی خودکار از کانال تلگرام سبک میم",
        "",
        "👇 لینک کانال اصلی:",
        "https://t.me/sabok_meme",
        "",
        "🔔 سابسکرایب کنید برای ویدیوهای بیشتر!",
        "",
        " ".join(selected_tags)
    ])
    return title, description
