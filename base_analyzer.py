from screenshot_handler import ScreenshotHandler
import csv


def parse_csv(filename: str, rows_to_parse: int) -> list:
    """
    Parse a CSV file and return its contents as a list of dictionaries.
    Each dictionary represents one row with keys from the header.
    """
    data = []
    try:
        with open(filename, "r", newline="", encoding="utf-8") as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for i, row in enumerate(csv_reader):
                if i >= rows_to_parse:
                    break
                data.append(row)
        return data
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return []
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return []


if __name__ == "__main__":
    CSV_PATH = "./military_bases.csv"
    ROWS_TO_PROCESS = 5

    screenshot_handler = ScreenshotHandler()
    military_bases = parse_csv(CSV_PATH, ROWS_TO_PROCESS)
    for base in military_bases:
        screenshot_handler.screenshot(
            latitude=base["latitude"], longitude=base["longitude"]
        )
    screenshot_handler.quit()
