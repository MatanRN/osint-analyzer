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
You are a seasoned Senior Intelligence Analyst specializing in satellite imagery interpretation for the US Army. Your mission is critical. We have credible intelligence indicating this area is a significant military base/facility of {self.country}.

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
        things_to_examine_list = results["things_to_continue_analyzing"]
        things_to_examine_str = "\n".join(
            f"- {item}" for item in things_to_examine_list
        )  # Format as a list

        previous_analysis_prompt = f"""

Here is the analysis of previous analyst {analyst_index+1} about this area and their recommendations. You can use this data but don’t use it as fact, think for yourself:
Analysis:
{analysis}
Things to examine:
{things_to_examine_str}
"""
        self.prompt += previous_analysis_prompt
