import os

import dotenv

from screenshot_handler import ScreenshotHandler
from utils_handler import parse_csv
from llm_analyst import Analyst

# Load environment variables from .env file
dotenv.load_dotenv("./.env")

# Get API key from environment variables
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing in the environment variables.")


def main():
    csv_path = "./military_bases.csv"
    rows_to_process = 1

    screenshot_handler = ScreenshotHandler()
    analyst = Analyst(api_key=API_KEY)
    military_bases = parse_csv(csv_path, rows_to_process)

    analysis_results = []

    for base in military_bases:
        screenshot = screenshot_handler.screenshot(
            latitude=base["latitude"], longitude=base["longitude"]
        )
        screenshot_analysis = analyst.analyze_image(
            image=screenshot, country=base["country"]
        )
        analysis_results.append(screenshot_analysis)
        print(screenshot_analysis)

    screenshot_handler.quit()


if __name__ == "__main__":
    main()
