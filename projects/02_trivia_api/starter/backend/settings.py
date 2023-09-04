from dotenv import load_dotenv
import os
load_dotenv()
DB_NAME = os.environ.get("DB_NAME")
DB_USER =os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

TEST_DB_NAME = os.environ.get("TEST_DB_NAME")
TEST_DB_USER = os.environ.get("TEST_DB_USER")
TEST_DB_PASSWORD = os.environ.get("TEST_DB_PASSWORD")