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


def team_analysis(screenshot_handler, analyst, base, team_size=8):
    latitude = float(base["latitude"])
    longitude = float(base["longitude"])
    distance_to_ground = 20000

    for i in range(team_size):
        screenshot = screenshot_handler.screenshot(
            latitude=latitude, longitude=longitude, ground_distance=distance_to_ground
        )
        screenshot_analysis = analyst.analyze_image(image=screenshot)
        print(f"command:{screenshot_analysis['action']}")
        match screenshot_analysis["action"]:
            case "zoom-in":
                distance_to_ground -= 3000
            case "zoom-out":
                distance_to_ground += 3000
            case "move-left":
                longitude -= 0.01
            case "move-right":
                longitude += 0.01
            case "finish":
                break
            case _:
                raise RuntimeError(f"Unknown action: {screenshot_analysis.action}")

        analyst.append_results(analyst_index=i, results=screenshot_analysis)

    print(screenshot_analysis)


def main():
    csv_path = "./military_bases.csv"
    rows_to_process = 2
    military_bases = parse_csv(csv_path, rows_to_process)
    screenshot_handler = ScreenshotHandler()

    base = military_bases[1]
    analyze_country = base["country"]
    analyst = Analyst(api_key=API_KEY, country=analyze_country)
    team_analysis(screenshot_handler=screenshot_handler, analyst=analyst, base=base)

    screenshot_handler.quit()


if __name__ == "__main__":
    main()
