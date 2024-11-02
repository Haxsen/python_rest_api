import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
RUST_SERVICE_URL = os.getenv("RUST_SERVICE_URL", "http://localhost:8081")
