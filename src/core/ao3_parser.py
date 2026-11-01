import requests
from bs4 import BeautifulSoup

class AO3Parser:
    def __init__(self, timeout=30):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'AO3Time/0.1'})
        self.timeout = timeout
    
    def fetch(self, url):
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        title = soup.select_one('h2.title.heading')
        title_text = title.get_text(strip=True) if title else 'untitled'
        return {'title': title_text, 'html': r.text}
