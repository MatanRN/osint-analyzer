from openai import OpenAI


class Commander:
    """
    Represents a commander AI that synthesizes analyses from multiple Analyst instances.

    The Commander inherits from the Analyst class and uses its underlying Gemini model
    to provide a final ruling based on a history of analyses. It takes a list of
    results from previous Analyst instances and incorporates them into its prompt.

    Attributes:
        prompt (str): The prompt string used to instruct the LLM, which includes
                    a summary of previous analyst reports.
    """

    def __init__(
        self,
        api_key: str,
        analyst_results: list,
        model: str = "deepseek/deepseek-r1:free",
    ):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = model
        self.system_prompt = """You are a highly experienced and decisive US Army Commander. Your mission is to synthesize intelligence reports from your team of analysts who have been investigating a potential enemy base or facility.
Review the provided analyst reports carefully. Your final output should be a concise and direct ruling or assessment of the situation based *only* on the information presented in these reports.
Focus on actionable intelligence and the most critical findings. Avoid speculation beyond what the reports support."""
        self.analyst_results_text = _parse_analyst_results(analyst_results)

    def analyze(self):
        """
        Generates a final ruling by the Commander based on the aggregated analyst reports.

        This method sends the compiled prompt (which includes the history of analyst findings)
        to the Gemini model and returns the model's textual response.

        Returns:
            str: The textual response from the Gemini model, representing the Commander's
                final ruling or synthesis of the analyses.
        """
        user_prompt = f"""Commander, here is the consolidated report from your analysts regarding the suspected enemy area:

{self.analyst_results_text}

Based on these findings, provide your final ruling."""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error during API call: {e}")
            return "Error: Could not get a response from the commander model."


def _parse_analyst_results(results: dict) -> str:
    analyses_string = ""
    # 'analyst_name' will be the key, e.g., "Analyst 1"
    for i, analyst_name in enumerate(results):
        # Get the actual analysis data dictionary using the key
        analysis_data = results[analyst_name]
        # Get the 'analysis' text from this dictionary,
        analysis_text = analysis_data.get("analysis")

        analyses_string += f"""
        {analyst_name}:
            - Analysis: {analysis_text}
"""
    return analyses_string
