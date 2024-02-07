import os
from dotenv import load_dotenv

load_dotenv()

WEB3_PROVIDER_URI = os.getenv("WEB3_PROVIDER_URI")
SMART_CONTRACT_ADDRESS = os.getenv("SMART_CONTRACT_ADDRESS")