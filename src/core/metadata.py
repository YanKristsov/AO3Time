import requests
from bs4 import BeautifulSoup

class MetadataCollector:
    def __init__(self, timeout=30):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'AO3Time/0.1'})
        self.timeout = timeout
    
    def collect(self, url):
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        title = soup.select_one('h2.title.heading')
        title_text = title.get_text(strip=True) if title else ''
        words = ''
        for dt in soup.select('dl.stats dt'):
            if 'слов' in dt.get_text().lower() or 'words' in dt.get_text().lower():
                dd = dt.find_next_sibling('dd')
                if dd:
                    words = dd.get_text(strip=True)
        return {
            'Название': title_text,
            'Fandoms': [],
            'Rating': '',
            'Category': [],
            'Relationships': [],
            'Characters': [],
            'Additional Tags': [],
            'Words': words
        }
