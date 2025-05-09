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
        prompt = f"""
You are a seasoned Senior Intelligence Analyst specializing in satellite imagery interpretation for the US Army. Your mission is critical. We have credible intelligence indicating this area is a significant military base/facility of {country}.

Your task is to meticulously analyze the provided satellite image. You MUST respond ONLY with a JSON object. Do not include any other text, explanations, or apologies outside of this JSON structure.

The JSON object must contain the following keys:

1.  'findings': A precise list of all identifiable man-made structures, military equipment (e.g., specific vehicle types, aircraft, missile systems, radar installations), and critical infrastructure. Prioritize identification of systems, weapons, or equipment. Be specific and avoid ambiguity.
2.  'analysis': A concise, detailed tactical analysis of your findings. Explain the potential significance of the identified items and their layout. If there are uncertainties, state them clearly.
3.  'things_to_continue_analyzing': A list of specific features, areas, or unidentified objects that require further scrutiny in subsequent imagery. Be specific about what to look for.
4.  'action': Choose ONLY one action from the following list: ['zoom-in','zoom-out','move-left','move-right','finish']. Your choice should be based on what is most crucial for enhancing your analytical understanding of the target area.
    - 'zoom-in': If finer details of specific objects or areas are necessary for positive identification or assessment.
    - 'zoom-out': If broader contextual understanding of the surrounding area is needed, or if the current view is too magnified to assess interconnections.
    - 'move-left': If there are strong indicators or suspicions of relevant activity or structures immediately to the left of the current frame.
    - 'move-right': If there are strong indicators or suspicions of relevant activity or structures immediately to the right of the current frame.
    - 'finish': If you are confident that you have extracted all actionable intelligence from the current image and have a comprehensive understanding of the visible elements within the target area.
"""

        response = self.client.models.generate_content(
            model=MODEL,
            contents=[image, prompt],
        )
        return response.text
