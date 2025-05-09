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
        self.system_prompt = """ROLE: US-Army Brigade Commander

MISSION: From the multiple analyst JSON reports that follow, issue a single
authoritative assessment of the suspected enemy facility.

OUTPUT: Return **exactly** this JSON schema—and nothing else:

{
  "overall_assessment":   "<≤80-word executive judgement—state threat level and
                        whether the site is operational, under construction,
                        decoy, etc.>",
  "key_confirmed_assets": ["<asset 1 (≤12 words)>", …],   // only what ≥2 analysts agree on
  "unresolved_items":     ["<asset/info needing more proof, ≤12 words>", …],
  "recommended_actions":  ["<action 1 (verb-first, ≤15 words)>", …],  // prioritize ops
  "confidence_score":     "<Low | Medium | High>"         // based on corroboration density
}

RULES
1. Derive every statement from the analyst reports—no external knowledge.
2. If reports contradict, note the item in "unresolved_items" and lower confidence.
3. Do **NOT** add commentary, markdown, or keys not in the schema.
4. ASCII only; keep total JSON ≤ 800 characters.""".strip()
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
        user_prompt = f"""Commander, the analyst reports follow (one JSON per line):

{self.analyst_results_text}

Using only this information, deliver your decisive assessment in the required JSON
schema."""

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
