import requests
from bs4 import BeautifulSoup

class FichubClient:
    def __init__(self, timeout=30):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'AO3Time/0.1'})
        self.timeout = timeout
    
    def get_work(self, url):
        try:
            r = self.session.get(url, timeout=self.timeout)
            r.raise_for_status()
            return r.text
        except Exception:
            return None
