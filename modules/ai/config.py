import os

from dotenv import dotenv_values


config = dotenv_values(".env")

OPENAI_API_KEY = config["OPENAI_API_KEY"]
