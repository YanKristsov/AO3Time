import requests
from bs4 import BeautifulSoup
import re

class MetadataCollector:
    def __init__(self, timeout=30):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'AO3Time/0.1'})
        self.timeout = timeout
    
    def collect(self, url):
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        # placeholders
        return {
            'Название': '',
            'Fandoms': [],
            'Rating': '',
            'Category': [],
            'Relationships': [],
            'Characters': [],
            'Additional Tags': [],
            'Words': ''
        }
