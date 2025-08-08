from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from metadata_generator import generate_metadata

class YouTubeUploader:
    def __init__(self):
        self.creds = Credentials.from_authorized_user_file('token.json')
        self.youtube = build('youtube', 'v3', credentials=self.creds)
        self.quota_used = 0

    def check_quota(self):
        if self.quota_used + 1600 > 10000:
            raise Exception("سهمیه روزانه یوتیوب تمام شده")

    def upload_video(self, video_path):
        self.check_quota()
        title, description = generate_metadata()
        request_body = {
            'snippet': {
                'title': f"{title} #Shorts",
                'description': description,
                'tags': ['meme', 'funny', 'telegram', 'shorts'],
                'categoryId': '23'
            },
            'status': {
                'privacyStatus': 'public',
                'selfDeclaredMadeForKids': False
            }
        }
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype='video/mp4')
        request = self.youtube.videos().insert(part='snippet,status', body=request_body, media_body=media)

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"آپلود شده: {int(status.progress() * 100)}%")

        self.quota_used += 1600
        print(f"آپلود کامل! Video ID: {response['id']}")
        return response
