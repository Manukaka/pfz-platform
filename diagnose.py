#!/usr/bin/env python3
"""
SAMUDRA AI — Diagnostic Tool

Identifies and fixes common startup issues
"""

import os
import sys
import subprocess
import socket
from pathlib import Path

class C:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def check_python():
    print(f"{C.BLUE}Checking Python...{C.END}")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(f"{C.GREEN}✅ Python {version.major}.{version.minor}{C.END}\n")
        return True
    print(f"{C.RED}❌ Python {version.major}.{version.minor} (need 3.11+){C.END}\n")
    return False

def check_dependencies():
    print(f"{C.BLUE}Checking dependencies...{C.END}")
    required = ['flask', 'numpy', 'scipy', 'requests']
    missing = []

    for pkg in required:
        try:
            __import__(pkg)
            print(f"{C.GREEN}✅ {pkg}{C.END}")
        except ImportError:
            print(f"{C.RED}❌ {pkg} (missing){C.END}")
            missing.append(pkg)

    if missing:
        print(f"\n{C.YELLOW}Installing missing packages...{C.END}")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install',
                'flask', 'numpy', 'scipy', 'requests', 'python-dotenv'
            ])
            print(f"{C.GREEN}✅ Installed{C.END}\n")
            return True
        except:
            print(f"{C.RED}❌ Installation failed{C.END}\n")
            return False

    print(f"{C.GREEN}✅ All dependencies installed{C.END}\n")
    return True

def check_port():
    print(f"{C.BLUE}Checking port 5000...{C.END}")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 5000))
        sock.close()

        if result == 0:
            print(f"{C.RED}❌ Port 5000 is in use!{C.END}")
            print(f"   Try: python -m flask run --port 5001\n")
            return False
        else:
            print(f"{C.GREEN}✅ Port 5000 is available{C.END}\n")
            return True
    except:
        print(f"{C.GREEN}✅ Port 5000 is available{C.END}\n")
        return True

def check_flask():
    print(f"{C.BLUE}Testing Flask import...{C.END}")

    try:
        from flask import Flask
        print(f"{C.GREEN}✅ Flask imports successfully{C.END}\n")
        return True
    except Exception as e:
        print(f"{C.RED}❌ Flask import error: {e}{C.END}\n")
        return False

def check_app():
    print(f"{C.BLUE}Testing app startup...{C.END}")

    try:
        from app.api import app
        print(f"{C.GREEN}✅ App loads successfully{C.END}")

        # Test a request
        with app.test_client() as client:
            response = client.get('/api/health')
            if response.status_code == 200:
                print(f"{C.GREEN}✅ API responds correctly{C.END}\n")
                return True
            else:
                print(f"{C.YELLOW}⚠️  API returned {response.status_code}{C.END}\n")
                return False
    except Exception as e:
        print(f"{C.RED}❌ App error: {e}{C.END}\n")
        import traceback
        print(traceback.format_exc())
        return False

def check_static_files():
    print(f"{C.BLUE}Checking static files...{C.END}")

    required_files = [
        'app/static/index.html',
        'app/static/styles.css',
        'app/static/app.js'
    ]

    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"{C.GREEN}✅ {file}{C.END}")
        else:
            print(f"{C.RED}❌ {file} (missing){C.END}")
            all_exist = False

    print()
    return all_exist

def main():
    print(f"\n{C.BOLD}{C.BLUE}{'='*60}{C.END}")
    print(f"{C.BOLD}{C.BLUE}SAMUDRA AI — Diagnostic Tool{C.END}")
    print(f"{C.BOLD}{C.BLUE}{'='*60}{C.END}\n")

    checks = [
        ("Python", check_python),
        ("Dependencies", check_dependencies),
        ("Static Files", check_static_files),
        ("Port 5000", check_port),
        ("Flask", check_flask),
        ("App", check_app),
    ]

    results = {}
    for name, check in checks:
        try:
            results[name] = check()
        except Exception as e:
            print(f"{C.RED}❌ {name}: {e}{C.END}\n")
            results[name] = False

    # Summary
    print(f"{C.BOLD}{C.BLUE}{'='*60}{C.END}")
    print(f"{C.BOLD}Summary:{C.END}")
    print(f"{C.BLUE}{'='*60}{C.END}\n")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = f"{C.GREEN}✅{C.END}" if result else f"{C.RED}❌{C.END}"
        print(f"{status} {name}")

    print()

    if passed == total:
        print(f"{C.GREEN}{C.BOLD}🎉 Everything checks out!{C.END}\n")
        print(f"Start the server with:")
        print(f"  {C.BOLD}python -m flask run{C.END}\n")
        print(f"Then open: http://localhost:5000\n")
        return 0
    else:
        print(f"{C.RED}{C.BOLD}⚠️  Issues found above{C.END}\n")
        print(f"Try:")
        print(f"  1. pip install -r requirements.txt")
        print(f"  2. python -m flask run\n")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"{C.RED}Error: {e}{C.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
