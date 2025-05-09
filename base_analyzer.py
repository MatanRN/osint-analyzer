import os
import json

import dotenv

from screenshot_handler import ScreenshotHandler
from utils_handler import parse_csv
from llm_analyst import Analyst
from llm_commander import Commander

# Load environment variables from .env file
dotenv.load_dotenv("./.env")

# Get API key from environment variables
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
if not (GEMINI_KEY or OPENROUTER_KEY):
    raise RuntimeError("A key is missing in the environment variables.")


def team_analysis(screenshot_handler, analyst, base, team_size=8):
    latitude = float(base["latitude"])
    longitude = float(base["longitude"])
    distance_to_ground = 20000

    analyses = {}

    for i in range(team_size):
        screenshot = screenshot_handler.screenshot(
            latitude=latitude, longitude=longitude, ground_distance=distance_to_ground
        )
        screenshot_analysis = analyst.analyze_image(image=screenshot)
        analyses[f"Analyst {i+1}"] = screenshot_analysis

        print(f"command:{screenshot_analysis['action']}")
        match screenshot_analysis["action"]:
            case "zoom-in":
                distance_to_ground -= 5000
            case "zoom-out":
                distance_to_ground += 5000
            case "move-left":
                longitude -= 0.01
            case "move-right":
                longitude += 0.01
            case "finish":
                break
            case _:
                raise RuntimeError(f"Unknown action: {screenshot_analysis.action}")

        analyst.append_results(analyst_index=i, results=screenshot_analysis)

    commander = Commander(api_key=OPENROUTER_KEY, analyst_results=analyses)
    verdict = commander.analyze()

    analyses["Commander"] = {"analysis": verdict}
    print(f"Commander Verdict:{verdict}")

    return analyses


def main():
    csv_path = "./military_bases.csv"
    rows_to_process = 2
    military_bases = parse_csv(csv_path, rows_to_process)
    screenshot_handler = ScreenshotHandler()

    base_analyses = []
    for base in military_bases:
        analyze_country = base["country"]
        analyst = Analyst(api_key=GEMINI_KEY, country=analyze_country)
        base_analyses.append(
            team_analysis(
                screenshot_handler=screenshot_handler, analyst=analyst, base=base
            )
        )
    bases_data = json.dumps(base_analyses, indent=4)

    output_file_path = "data.json"
    with open(output_file_path, "w") as f:
        f.write(bases_data)
    print(f"Analysis data saved to {output_file_path}")

    screenshot_handler.quit()


if __name__ == "__main__":
    main()
