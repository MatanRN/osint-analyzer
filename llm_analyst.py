import json

from google import genai


class Analyst:
    """
    Represents an AI analyst that uses a Gemini model to analyze satellite images.

    The analyst is initialized with an API key and a target country. It can then
    analyze images to identify military structures and equipment, and its prompt
    can be updated with results from previous analyses to build context.

    Attributes:
        client: A genai.Client instance for interacting with the Gemini API.
        model:
        prompt: A string template used to instruct the Gemini model on how to
                analyze images and format its response.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash", country=None):
        self.client = genai.Client(api_key=api_key)
        self.country = country
        self.model = model
        self.prompt = f"""
You are an expert in understanding satellite imagery and you work for the US army. We got
intel that this area is a base/facility of the military of {country}. Analyze this image and
respond ONLY with a JSON object containing the following keys:
1.'findings': A list of findings that you think are important for the US army to know, including
all man-made structures, military equipment, and infrastructure. We are trying to find which
systems, weapons, or equipment are present so focus on that.
2.'analysis': A detailed analysis of your findings.
3.'things_to_continue_analyzing': A list of things that you think are important to continue analyzing in further images. Mention its general position in the image.
4.'action': One of ['zoom-in','zoom-out','move-left','move-right','finish'] based on what would help you analyze the image or area better.
- Choose 'zoom-in' if you need to zoom in the image
- Choose 'zoom-out' if you need more context of the surrounding area or if you are zoomed
in too much.
- Choose 'move-left' or 'move-right' if you suspect there are important features just outside
the current view.
- Choose 'finish' if you have a complete understanding of the location.
"""

    def analyze_image(self, image):
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
            model=self.model,
            contents=[image, self.prompt],
        )
        # Extract JSON string from Markdown code block
        json_string = response.text
        if json_string.startswith("```json"):
            json_string = json_string[7:]  # Remove ```json\n
        if json_string.endswith("```"):
            json_string = json_string[:-3]  # Remove ```

        response_json = json.loads(json_string.strip())
        return response_json

    def append_results(self, analyst_index: int, results: dict):
        """
        Appends the analysis and recommendations from a previous analyst to the current prompt.

        This method takes the results from a previous analysis step, formats them,
        and adds them to the existing `self.prompt`. This provides context to the
        LLM for subsequent analysis, encouraging it to build upon previous findings
        while still thinking critically.

        Args:
            analyst_index: The index or identifier of the previous analyst/analysis step.
            results: A dictionary containing the 'analysis' and 'things_to_continue_analyzing'
                    from the previous step.
        """
        analysis = results["analysis"]

        previous_analysis_prompt = f"""
-------------------------------------
Analysis by Analyst {analyst_index+1}:
    Analysis:
        {results["analysis"]}
    Things to continue analyzing:
        {results["things_to_continue_analyzing"]}
"""
        self.prompt += previous_analysis_prompt
