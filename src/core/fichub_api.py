import requests

class FichubAPI:
    def __init__(self, timeout=60):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'AO3Time/0.1'})
        self.timeout = timeout
        self.base = 'https://fichub.net'
    
    def get_epub(self, url):
        try:
            r = self.session.get(f'{self.base}/api/v0/epub', params={'q': url}, timeout=self.timeout)
            r.raise_for_status()
            data = r.json()
            epub_path = data.get('urls', {}).get('epub') or data.get('epub_url')
            if not epub_path:
                return None
            file_url = self.base + epub_path
            rf = self.session.get(file_url, timeout=self.timeout)
            rf.raise_for_status()
            return rf.content, data.get('meta', {}).get('title', 'work')
        except Exception:
            return None
