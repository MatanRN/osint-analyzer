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
    """
    Conducts a multi-step analysis of a given base using a team of virtual analysts.

    The function simulates a team of analysts examining a geographical location (base).
    Each analyst takes a screenshot, analyzes it, and suggests an action (zoom, move, finish).
    The process iterates, adjusting the view based on analyst actions, until an analyst
    decides to 'finish' or the team_size limit is reached.
    Finally, a commander synthesizes all analyst reports into a final verdict.

    Args:
        screenshot_handler: An instance of ScreenshotHandler to capture images.
        analyst: An instance of the Analyst class to perform image analysis.
        base: A dictionary containing base information, including 'latitude',
            'longitude', and 'country'.
        team_size (int, optional): The maximum number of analyst iterations.
                                Defaults to 8.

    Returns:
        dict: A dictionary containing all analyses, including individual analyst
            reports and the final commander's verdict.
    """
    latitude = float(base["latitude"])
    longitude = float(base["longitude"])
    base_id = f"{latitude}_{longitude}_{base['country']}"
    distance_to_ground = 20000

    analyses = {}

    for i in range(team_size):
        screenshot = screenshot_handler.screenshot(
            latitude=latitude,
            longitude=longitude,
            ground_distance=distance_to_ground,
            filename=f"{base_id}/analyst_{i+1}",
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
    if verdict == "":
        raise RuntimeError("LLM Analysis Error")

    analyses["Commander"] = json.loads(verdict.strip())
    return analyses


def analyze_bases(csv_path: str = "./military_bases.csv", rows_to_process=8):
    military_bases = parse_csv(csv_path, rows_to_process)
    screenshot_handler = ScreenshotHandler()

    # Load existing analyses if the file exists
    output_file_path = "data.json"
    existing_analyses = []
    if os.path.exists(output_file_path):
        try:
            with open(output_file_path, "r") as f:
                existing_analyses = json.load(f)
                print(f"Loaded {len(existing_analyses)} existing analyses")
        except json.JSONDecodeError:
            print(f"Error loading {output_file_path}, starting with empty analyses")

    # Create a set of already analyzed base identifiers (latitude_longitude_country)
    analyzed_bases = {
        f"{base_data.get('latitude', '')}_{base_data.get('longitude', '')}_{base_data.get('country', '')}"
        for analysis in existing_analyses
        for base_data in [analysis.get("base_info", {})]
    }

    base_analyses = existing_analyses.copy()

    for base in military_bases:

        # Create identifier for current base
        base_id = f"{base.get('latitude', '')}_{base.get('longitude', '')}_{base.get('country', '')}"
        # Skip if this base has already been analyzed
        if base_id in analyzed_bases:
            print(f"Skipping already analyzed base: {base_id}")
            continue
        # create directory if it doesn't exist
        os.makedirs(f"./screenshots/{base_id}", exist_ok=True)
        # if exist_ok remove all files in the directory
        for filename in os.listdir(f"./screenshots/{base_id}"):
            file_path = os.path.join(f"./screenshots/{base_id}", filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        print(f"Analyzing base: {base_id}")
        analyze_country = base["country"]
        analyst = Analyst(api_key=GEMINI_KEY, country=analyze_country)

        # Perform analysis
        analysis_result = team_analysis(
            screenshot_handler=screenshot_handler, analyst=analyst, base=base
        )

        # Add base information to the result for future identification
        analysis_result["base_info"] = {
            "latitude": base["latitude"],
            "longitude": base["longitude"],
            "country": base["country"],
        }

        # Add to our analyses list
        base_analyses.append(analysis_result)

        bases_data = json.dumps(base_analyses, indent=4)

        # Save after each analysis to preserve progress
        temp_data = json.dumps(base_analyses, indent=4)
        with open(output_file_path, "w") as f:
            f.write(temp_data)
        print(f"Updated analysis data saved to {output_file_path}")

    # Final save (may be redundant but ensures consistency)
    bases_data = json.dumps(base_analyses, indent=4)
    with open(output_file_path, "w") as f:
        f.write(bases_data)
    print(f"Analysis data saved to {output_file_path}")

    screenshot_handler.quit()


if __name__ == "__main__":
    analyze_bases()
