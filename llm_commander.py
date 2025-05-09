from llm_analyst import Analyst


class Commander(Analyst):
    """
    Represents a commander AI that synthesizes analyses from multiple Analyst instances.

    The Commander inherits from the Analyst class and uses its underlying Gemini model
    to provide a final ruling based on a history of analyses. It takes a list of
    results from previous Analyst instances and incorporates them into its prompt.

    Attributes:
        prompt (str): The prompt string used to instruct the LLM, which includes
                    a summary of previous analyst reports.
    """

    def __init__(self, api_key: str, analyst_results: list):
        super().__init__(api_key)
        self.prompt = f"""You are a commander of military analysts and you are investigating something that intel said
is probably an enemy base/area. Here is the history of what the analysts said (each one was
written by a different analyst).{_parse_analyst_results(analyst_results)} Return a final ruling based on the analysis historu"""

    def analyze(self):
        """
        Generates a final ruling by the Commander based on the aggregated analyst reports.

        This method sends the compiled prompt (which includes the history of analyst findings)
        to the Gemini model and returns the model's textual response.

        Returns:
            str: The textual response from the Gemini model, representing the Commander's
                final ruling or synthesis of the analyses.
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=[self.prompt],
        )
        # Extract JSON string from Markdown code block
        return response.text


def _parse_analyst_results(results: list) -> str:
    analyses_string = ""
    for i, result in enumerate(results):
        analysis = result.get("analysis")
        analyses_string += f"""
        Analyst {i+1}:
            - {analysis}
        
"""
    return analyses_string
