import json

from google import genai

from spite.config import get_settings

settings = get_settings()

SCORING_PROMPT = """
You are a senior developer with 15 years of experience who has seen far too many
ridiculous job offers. Your job is to analyze job vacancies and rate them
with brutal honesty.

SCORING CRITERIA (0.0 to 10.0):

PENALTIES (decrease score):
- "Startup environment" without mentioning compensation → -2 points
- More than 3 technologies required for a junior role → -1.5 points
- "Rockstar", "ninja", "evangelist" in the title → -2 points
- "Competitive salary" without a real number → -1.5 points
- 5+ years of experience for technologies less than 5 years old → -3 points
- "We're a family" → -1 point
- Contradictory requirements (junior with senior responsibilities) → -2 points
- Stack of 10+ required technologies → -1.5 points

BONUSES (increase score):
- Explicit salary in the ad → +2 points
- Clear and reasonable technical stack → +1 point
- Honest description of responsibilities → +1 point
- Explicit remote modality → +1 point
- Selection process described → +1 point

ANALYSIS:
Title: {title}
Company: {company}
Location: {location}
Salary: {salary}
Description: {description}

Respond ONLY with a valid JSON, no markdown, no explanations outside the JSON:
{{
    "score": <number between 0.0 and 10.0>,
    "summary": "<one line honestly describing the vacancy>",
    "red_flags": ["<flag 1>", "<flag 2>"],
    "green_flags": ["<flag 1>", "<flag 2>"],
    "reasoning": "<2-3 sentences explaining the score with constructive cynicism>"
}}
"""


class GeminiService:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = "gemini-2.0-flash"

    def score_job(
        self,
        title: str,
        company: str,
        description: str,
        location: str | None = None,
        salary: str | None = None,
    ) -> dict:
        prompt = SCORING_PROMPT.format(
            title=title,
            company=company,
            location=location or "Not specified",
            salary=salary or "Not specified (suspicious)",
            description=description or "No description. That says it all.",
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            raw = response.text.strip()

            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]

            result = json.loads(raw)
            result["score"] = max(0.0, min(10.0, float(result["score"])))
            return result

        except json.JSONDecodeError:
            return {
                "score": 5.0,
                "summary": "Error parsing Gemini response.",
                "red_flags": ["The AI had a bad day"],
                "green_flags": [],
                "reasoning": "Could not correctly analyze the vacancy.",
            }
        except Exception as e:
            return {
                "score": 0.0,
                "summary": f"Error: {str(e)}",
                "red_flags": ["Connection error with Gemini"],
                "green_flags": [],
                "reasoning": "Something went wrong. Check your API key.",
            }


gemini_service = GeminiService()
