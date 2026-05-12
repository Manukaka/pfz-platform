#!/usr/bin/env python3
"""
SAMUDRA AI — Quick Start Setup Helper

Interactive guide to get the system running in minutes
"""

import os
import sys
import subprocess
from pathlib import Path

# Colors
class C:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title):
    print(f"\n{C.BOLD}{C.BLUE}{'='*70}{C.END}")
    print(f"{C.BOLD}{C.BLUE}{title:^70}{C.END}")
    print(f"{C.BOLD}{C.BLUE}{'='*70}{C.END}\n")

def print_step(num, title):
    print(f"\n{C.BOLD}{C.BLUE}Step {num}: {title}{C.END}")
    print(f"{C.BLUE}{'-'*70}{C.END}")

def check_python():
    """Check Python version"""
    print_step(1, "Checking Python")

    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(f"{C.GREEN}✅ Python {version.major}.{version.minor}.{version.micro}{C.END}")
        return True
    else:
        print(f"{C.YELLOW}⚠️  Python {version.major}.{version.minor} found (3.11+ required){C.END}")
        print(f"   Download Python 3.11+: https://www.python.org/downloads/")
        return False

def check_dependencies():
    """Check if dependencies are installed"""
    print_step(2, "Checking Dependencies")

    required = [
        'flask',
        'numpy',
        'scipy',
        'requests',
        'python-dotenv'
    ]

    missing = []
    for pkg in required:
        try:
            __import__(pkg)
            print(f"{C.GREEN}✅ {pkg}{C.END}")
        except ImportError:
            print(f"{C.YELLOW}❌ {pkg} (not installed){C.END}")
            missing.append(pkg)

    if missing:
        print(f"\n{C.YELLOW}Installing missing packages...{C.END}")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install',
                'flask', 'numpy', 'scipy', 'requests', 'python-dotenv'
            ])
            print(f"{C.GREEN}✅ All dependencies installed{C.END}")
            return True
        except subprocess.CalledProcessError:
            print(f"{C.YELLOW}⚠️  Could not install dependencies automatically{C.END}")
            print(f"   Try: pip install -r requirements.txt")
            return False

    print(f"{C.GREEN}✅ All dependencies installed{C.END}")
    return True

def setup_env():
    """Set up .env file"""
    print_step(3, "Setting Up Environment")

    env_file = Path('.env')
    example_file = Path('.env.example')

    if env_file.exists():
        print(f"{C.GREEN}✅ .env file exists{C.END}")
        print(f"   Edit it to add real API credentials")
        return True

    if example_file.exists():
        print(f"Creating .env from template...")
        with open(example_file) as f:
            content = f.read()
        with open(env_file, 'w') as f:
            f.write(content)
        print(f"{C.GREEN}✅ Created .env file{C.END}")
        print(f"   Edit to add your API credentials")
        return True

    print(f"{C.YELLOW}⚠️  .env.example not found{C.END}")
    print(f"   The system will use defaults")
    return True

def test_flask():
    """Test if Flask starts"""
    print_step(4, "Testing Flask")

    try:
        from app.api import app
        print(f"{C.GREEN}✅ Flask imported successfully{C.END}")

        # Try creating test app context
        with app.test_client() as client:
            response = client.get('/api/health')
            if response.status_code == 200:
                print(f"{C.GREEN}✅ API responds{C.END}")
                return True
            else:
                print(f"{C.YELLOW}⚠️  API returned {response.status_code}{C.END}")
                return False
    except Exception as e:
        print(f"{C.YELLOW}⚠️  Error: {str(e)}{C.END}")
        return False

def show_next_steps():
    """Show next steps"""
    print_header("Ready to Go!")

    print(f"{C.GREEN}✅ SAMUDRA AI is set up and ready{C.END}\n")

    print(f"{C.BOLD}Next Steps:{C.END}\n")

    print(f"{C.BLUE}1. Start the server:{C.END}")
    print(f"   flask run\n")

    print(f"{C.BLUE}2. Open in browser:{C.END}")
    print(f"   http://localhost:5000\n")

    print(f"{C.BLUE}3. (Optional) Test the system:{C.END}")
    print(f"   python test_api.py\n")

    print(f"{C.BLUE}4. (For real data) Set up API credentials:{C.END}")
    print(f"   - Edit .env with credentials from:")
    print(f"   - CMEMS: https://data.marine.copernicus.eu/")
    print(f"   - NASA: https://earthdata.nasa.gov/")
    print(f"   - ECMWF: https://cds.climate.copernicus.eu/")
    print(f"   - Then: python validate_credentials.py\n")

    print(f"{C.BLUE}5. Learn more:{C.END}")
    print(f"   - README.md — System overview")
    print(f"   - REAL_DATA_INTEGRATION.md — Real data setup (5 min)")
    print(f"   - API_SETUP_GUIDE.md — Detailed API guide")
    print(f"   - TESTING_GUIDE.md — Testing guide\n")

def main():
    print_header("SAMUDRA AI — Quick Start Setup")

    steps = [
        ("Python", check_python),
        ("Dependencies", check_dependencies),
        ("Environment", setup_env),
        ("Flask", test_flask),
    ]

    all_ok = True
    for name, check in steps:
        try:
            result = check()
            if not result:
                all_ok = False
        except Exception as e:
            print(f"{C.YELLOW}❌ {name}: {e}{C.END}")
            all_ok = False

    print()

    if all_ok:
        show_next_steps()
        return 0
    else:
        print(f"{C.YELLOW}⚠️  Some issues found. See above for details.{C.END}")
        print(f"{C.YELLOW}Try: pip install -r requirements.txt{C.END}\n")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}Setup cancelled{C.END}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{C.YELLOW}Error: {e}{C.END}\n")
        sys.exit(1)
