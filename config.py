import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = -1002555456158
DONOR_TOPIC_ID = 2
BENEFICIARY_TOPIC_ID = 3
STOP_TOPIC = 168
ERRORS_TOPIC = 574  
SUPPORT_TOPIC = 882  

BANNED_USERS_FILE = "banned_users.json"