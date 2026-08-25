#!/usr/bin/env python3
"""Contact Scraper Pro - Main Entry Point"""
import os, sys, time, json, signal
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    missing = []
    try:
        import requests
    except ImportError:
        missing.append('requests')
    try:
        import pandas
    except ImportError:
        missing.append('pandas')
    try:
        import bs4
    except ImportError:
        missing.append('beautifulsoup4')
    
    if missing:
        print(f'Missing dependencies: {", ".join(missing)}')
        print('Installing...')
        os.system(f'{sys.executable} -m pip install {" ".join(missing)}')
        print('Installation complete!\n')

def main():
    print('=' * 60)
    print('          CONTACT SCRAPER PRO')
    print('=' * 60)
    
    check_dependencies()
    
    print('\nSelect mode:')
    print('1. CLI Scraper (Terminal)')
    print('2. Web Interface (Browser)')
    print('3. Tor Scraper (Anonymous)')
    print('4. Exit')
    
    choice = input('\nEnter choice (1-4): ').strip()
    
    if choice == '1':
        from scraper_cli import run_cli
        run_cli()
    elif choice == '2':
        from web_server import run_server
        run_server()
    elif choice == '3':
        from tor_scraper import run_tor
        run_tor()
    elif choice == '4':
        print('Goodbye!')
        sys.exit(0)
    else:
        print('Invalid choice!')
        main()

if __name__ == '__main__':
    main()
