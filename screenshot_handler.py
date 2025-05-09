import os
import time
from io import BytesIO

from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait


class ScreenshotHandler:
    def __init__(self, options=None):
        """
        Initialize the screenshot handler with optional Chrome options.

        Args:
            options: Optional Chrome options for the WebDriver
        """
        chrome_options = ChromeOptions() if options is None else options

        self.driver = webdriver.Chrome(options=chrome_options)

        # Create screenshots directory if it doesn't exist
        os.makedirs("screenshots", exist_ok=True)

    def __wait_for_page_load(self, timeout=10):
        """
        Wait for page to load completely.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            bool: True if page loaded successfully, False if timeout occurred
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            return True
        except TimeoutException:
            print("Timeout waiting for page to load")
            return False

    def screenshot(self, latitude: str, longitude: str, output_file_path: str = None):
        """
        Takes a screenshot of Google Earth at the specified coordinates.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            output_file_path: Optional custom file path for the screenshot

        Returns:
            PIL.Image: The cropped image if successful, None otherwise
        """

        image_width = 1024
        image_height = 1024

        if output_file_path is None:
            output_file_path = f"screenshots/location_{latitude}_{longitude}.jpeg"

        google_earth_url = (
            f"https://earth.google.com/web/@{latitude},{longitude},100a,20000d"
        )
        self.driver.get(google_earth_url)

        is_page_ready = self.__wait_for_page_load()
        if is_page_ready is not False:
            # Take screenshot - waiting a bit for Google Earth to load the coordinates
            time.sleep(5)
            # Get screenshot as PNG bytes
            png_data = self.driver.get_screenshot_as_png()

            # Convert PNG to JPEG using PIL
            img = Image.open(BytesIO(png_data))
            # Get dimensions of the full screenshot
            full_width, full_height = img.size

            # Calculate coordinates for center crop
            left = (full_width - image_width) // 2
            top = (full_height - image_height) // 2
            right = left + image_width
            bottom = top + image_height

            # Crop the image
            cropped_img = img.crop((left, top, right, bottom))

            # Convert to RGB and save
            cropped_img = cropped_img.convert("RGB")  # Remove alpha for JPEG
            cropped_img.save(output_file_path, "JPEG", quality=95)
            print(f"Screenshot saved to {output_file_path}")
            return cropped_img
        else:
            print(
                f"Error loading google earth for coordinates: lat:{latitude},long:{longitude}"
            )

    def quit(self):
        """Close the browser and release resources when done"""
        self.driver.quit()
