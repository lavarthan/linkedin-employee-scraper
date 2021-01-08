from linkedin_api import Linkedin
import os
from dotenv import load_dotenv

load_dotenv()
user_name = os.getenv("user_name")
password = os.getenv("password")
api = Linkedin(user_name, password)
