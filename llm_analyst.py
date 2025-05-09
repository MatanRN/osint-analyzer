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
SYSTEM (role):
You are a US-Army satellite-imagery analyst.

TASK (single image, suspected {country} military site):
Return **only** a strictly valid JSON object with **exactly** these keys ⬇️

1. "findings" – array of concise (< 25 words each) observations of man-made structures, weapons, vehicles, or support infrastructure visible in the frame.  
2. "analysis" – one paragraph, ≤ 120 words, explaining the operational significance of the findings (no copy-paste from bullets).  
3. "things_to_continue_analyzing" – array of < 15-word items that describe features worth inspecting in later images; include approximate image quadrant (e.g., "suspected SAM TEL, NE-quadrant").  
4. "action" – ONE of: "zoom-in", "zoom-out", "move-left", "move-right", "finish".  
   • Need finer detail → "zoom-in"  
   • Need more surrounding context → "zoom-out"  
   • Edge-hint of important feature → "move-left"/"move-right"  
   • Confident assessment complete → "finish"

RULES:  
A. You **may inspect prior-run analyses provided below**, but treat them as unverified; form your own judgment.  
B. Output nothing except the JSON (no commentary, no markdown).  
C. Keep total JSON length ≤ 900 characters.  
D. Do not invent objects; use "none" when a section is empty.  
E. Use double quotes around all keys and string values.  
F. ASCII only.

""".strip()

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

        previous_analysis_prompt = f"""
    "analyst":{analyst_index}
    "analysis":{results["analysis"]}
    "things_to_continue_analyzing":{results["things_to_continue_analyzing"]}
"""
        self.prompt += previous_analysis_prompt.strip()
