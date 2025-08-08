import json
import os
from datetime import datetime

class StateManager:
    def __init__(self, state_file='state.json'):
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'last_checked': None, 'last_processed_id': None, 'upload_count': 0, 'last_upload_date': None}

    def save_state(self):
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def get_new_messages(self, messages):
        """فقط پیام‌های جدید نسبت به آخرین پردازش شده"""
        if not self.state['last_processed_id']:
            return messages[:3]
        new_messages = []
        for msg in messages:
            if msg['id'] == self.state['last_processed_id']:
                break
            new_messages.append(msg)
        return new_messages[:5]

    def update_upload_stats(self):
        today = datetime.now().strftime('%Y-%m-%d')
        if self.state['last_upload_date'] == today:
            self.state['upload_count'] += 1
        else:
            self.state['upload_count'] = 1
            self.state['last_upload_date'] = today
        self.save_state()

    def can_upload_more(self, max_uploads=3):
        today = datetime.now().strftime('%Y-%m-%d')
        if self.state['last_upload_date'] != today:
            self.state['upload_count'] = 0
            self.state['last_upload_date'] = today
            self.save_state()
            return True
        return self.state['upload_count'] < max_uploads
