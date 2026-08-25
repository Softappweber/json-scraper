#!/usr/bin/env python3
"""Tor Scraper Module"""
import subprocess, sys, time, os
from scraper_cli import Scraper, save_contacts

def check_tor():
    """Check if Tor is installed"""
    try:
        result = subprocess.run(['tor', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def start_tor():
    """Start Tor service"""
    try:
        subprocess.Popen(['tor'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)
        return True
    except:
        return False

def setup_tor_proxy():
    """Setup Tor proxy environment"""
    os.environ['http_proxy'] = 'socks5h://127.0.0.1:9050'
    os.environ['https_proxy'] = 'socks5h://127.0.0.1:9050'
    os.environ['HTTP_PROXY'] = 'socks5h://127.0.0.1:9050'
    os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:9050'

def run_tor():
    print('\n' + '=' * 50)
    print('   Tor Scraper')
    print('=' * 50)
    
    if not check_tor():
        print('\n❌ Tor is not installed!')
        print('Install Tor: sudo apt-get install tor')
        print('Or download Tor Browser from https://www.torproject.org/')
        return
    
    print('\n✅ Tor detected')
    print('Starting Tor service...')
    
    if not start_tor():
        print('❌ Failed to start Tor')
        return
    
    print('✅ Tor started')
    setup_tor_proxy()
    print('✅ Proxy set to socks5h://127.0.0.1:9050')
    
    f = open('urls.txt') if os.path.exists('urls.txt') else None
    if f:
        urls = [l.strip() for l in f if l.strip() and not l.startswith('#')]
        f.close()
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
    
    print(f'\nScraping {len(urls)} URLs through Tor...')
    scraper = Scraper()
    contacts = scraper.scrape(urls, max_contacts=300, max_depth=3, delay=2)
    save_contacts(contacts)
    print(f'\nDone! Total: {len(contacts)} contacts')
