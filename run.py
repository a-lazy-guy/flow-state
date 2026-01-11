import sys
import os

# Add the current directory to sys.path to make the 'app' package importable
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import main

if __name__ == "__main__":
    main()
