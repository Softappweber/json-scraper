#!/usr/bin/env python3
"""CLI Scraper Module"""
import re, time, random, ssl, json
import urllib.request, urllib.parse
from datetime import datetime
from pathlib import Path

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15'
]

class Scraper:
    def __init__(self):
        self.contacts = []
        self.visited = set()
        self.emails_found = set()
        self.phones_found = set()
    
    def fetch(self, url, retries=3):
        for attempt in range(retries):
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                req = urllib.request.Request(url)
                req.add_header('User-Agent', random.choice(USER_AGENTS))
                req.add_header('Accept', 'text/html,application/xhtml+xml')
                resp = urllib.request.urlopen(req, timeout=15, context=ctx)
                return resp.read().decode('utf-8', errors='ignore')
            except:
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return None
        return None
    
    def extract_emails(self, html):
        emails = set()
        for m in re.findall(r'mailto:([^"\'?\s<>]+)', html, re.I):
            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', m):
                emails.add(m.lower())
        for m in re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html):
            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', m):
                emails.add(m.lower())
        return list(emails)
    
    def extract_phones(self, html):
        phones = set()
        for m in re.findall(r'tel:([^"\'?\s<>]+)', html, re.I):
            phones.add(m.strip())
        patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}',
            r'\+\d{10,13}',
            r'\(\d{3}\)\s?\d{3}-\d{4}'
        ]
        for p in patterns:
            for m in re.findall(p, html):
                phones.add(m.strip())
        return list(phones)
    
    def extract_links(self, html, base_url):
        links = set()
        base_domain = urllib.parse.urlparse(base_url).netloc
        for link in re.findall(r'href=["\']([^"\'#]+)["\']', html, re.I):
            if re.search(r'\.(jpg|jpeg|png|gif|pdf|zip|css|js)$', link, re.I):
                continue
            abs_url = urllib.parse.urljoin(base_url, link)
            if urllib.parse.urlparse(abs_url).netloc == base_domain:
                if re.search(r'contact|about|profile|supplier|seller|company|detail', abs_url, re.I):
                    links.add(abs_url)
        return list(links)
    
    def scrape(self, urls, max_contacts=300, max_depth=3, delay=1):
        all_contacts = []
        for url in urls:
            if len(all_contacts) >= max_contacts:
                break
            print(f'Scraping: {url}')
            self._scrape_page(url, max_depth, delay, all_contacts, max_contacts)
            time.sleep(delay)
        return all_contacts[:max_contacts]
    
    def _scrape_page(self, url, depth, delay, all_contacts, max_contacts):
        if url in self.visited or depth < 0 or len(all_contacts) >= max_contacts:
            return
        self.visited.add(url)
        html = self.fetch(url)
        if not html:
            return
        emails = self.extract_emails(html)
        phones = self.extract_phones(html)
        for i in range(max(len(emails), len(phones))):
            email = emails[i] if i < len(emails) else ''
            phone = phones[i] if i < len(phones) else ''
            if email in self.emails_found or phone in self.phones_found:
                continue
            if email:
                self.emails_found.add(email)
            if phone:
                self.phones_found.add(phone)
            all_contacts.append({
                'email': email,
                'phone': phone,
                'website': urllib.parse.urlparse(url).netloc,
                'source_url': url
            })
        if depth > 0:
            for link in self.extract_links(html, url)[:5]:
                time.sleep(delay)
                self._scrape_page(link, depth - 1, delay, all_contacts, max_contacts)


def save_contacts(contacts):
    if not contacts:
        print('No contacts!')
        return
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    Path('output').mkdir(exist_ok=True)
    if HAS_PANDAS:
        df = pd.DataFrame(contacts)
        df.to_csv(f'output/contacts_{ts}.csv', index=False, encoding='utf-8-sig')
        df.to_excel(f'output/contacts_{ts}.xlsx', index=False, engine='openpyxl')
        print(f'Saved: output/contacts_{ts}.csv')
        print(f'Saved: output/contacts_{ts}.xlsx')
    else:
        with open(f'output/contacts_{ts}.csv', 'w') as f:
            f.write('email,phone,website,source_url\n')
            for c in contacts:
                f.write(f"{c['email']},{c['phone']},{c['website']},{c['source_url']}\n")
        print(f'Saved: output/contacts_{ts}.csv')


def run_cli():
    print('\n' + '=' * 50)
    print('   CLI Scraper')
    print('=' * 50)
    
    f = Path('urls.txt')
    if f.exists():
        with open(f) as fp:
            urls = [l.strip() for l in fp if l.strip() and not l.startswith('#')]
    else:
        urls = []
    
    if not urls:
        print('\nEnter URLs (one per line, empty to finish):')
        while True:
            u = input().strip()
            if not u:
                break
            if not u.startswith(('http://', 'https://')):
                u = 'https://' + u
            urls.append(u)
        with open('urls.txt', 'w') as f:
            f.write('\n'.join(urls))
    
    print(f'\nFound {len(urls)} URLs')
    scraper = Scraper()
    contacts = scraper.scrape(urls, max_contacts=300, max_depth=3, delay=1)
    save_contacts(contacts)
    print(f'\nDone! Total: {len(contacts)} contacts')
