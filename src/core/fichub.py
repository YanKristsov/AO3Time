import re
import requests
from bs4 import BeautifulSoup

class FichubClient:
    def __init__(self, timeout=30):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'AO3Time/0.1'})
        self.timeout = timeout
    
    def get_pdf_url(self, url):
        # try fichub API style or direct page
        try:
            r = self.session.get(url, timeout=self.timeout)
            r.raise_for_status()
            return None
        except Exception:
            return None
