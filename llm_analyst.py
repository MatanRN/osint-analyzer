from google import genai

MODEL = "gemini-2.0-flash"


class Analyst:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def analyze_image(self, image, country):
        """
        Analyzes a satellite image to identify military structures and equipment.

        Uses Gemini AI model to analyze the provided image in the context of the specified
        country's military facilities. The model identifies potential military structures,
        equipment, and other significant features in the image.

        Args:
            image: Image data (PIL Image, bytes, or file path) to be analyzed
            country: String indicating the country whose military facilities are being examined

        Returns:
            str: Text analysis of the image containing findings about military structures,
                equipment, and other relevant observations
        """
        response = self.client.models.generate_content(
            model=MODEL,
            contents=[
                image,
                f"You are an expert in understanding satellite imagery and you work for the US army. We got intel that this area is a base/facility of the military of {country} . Analyze this image, try to find military devices, structures etc and tell me your findings",
            ],
        )
        return response.text
