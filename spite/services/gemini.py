import json

from google import genai

from spite.config import get_settings

settings = get_settings()

SCORING_PROMPT = """
Act as a Senior Software Engineer with 15+ years of experience who has seen it all and has zero patience for corporate nonsense. 
Analyze the following IT job vacancy and determine its level of coherence and quality.

EVALUATION CRITERIA (Internal):
- Tech Stack: Does it make sense or is it just a random wishlist of buzzwords?
- Seniority vs. Experience: Are the years of experience realistic for the role and salary?
- Transparency: Is the description clear or is it full of corporate "smoke" (e.g., "rockstar", "ninja", "we are a family", "wear many hats")?
- Red Flags: Is this a dignified offer or a disaster waiting to happen?

VACANCY DATA:
Title: {title}
Company: {company}
Location: {location}
Salary: {salary}
Description: {description}

OUTPUT INSTRUCTIONS:
1. "score": A number between 0.0 and 10.0.
2. "summary": One short, direct, and honest sentence about the offer, delivered with a touch of "porteño" sarcasm (blunt, cynical, and witty).

Respond ONLY with a valid JSON:
{{
    "score": <number>,
    "summary": "<string>"
}}
"""


class GeminiService:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = "gemini-2.5-flash"

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
                config={
                    "response_mime_type": "application/json",
                },
            )

            result = json.loads(response.text)

            result["score"] = max(0.0, min(10.0, float(result.get("score", 5.0))))
            return result

        except json.JSONDecodeError:
            return {
                "score": 5.0,
                "summary": "Error parsing Gemini response.",
            }
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                summary = "AI called in sick. Too many requests, try again in a minute."
            elif "API_KEY" in error_str or "401" in error_str:
                summary = "API key rejected. Even the AI doesn't trust you."
            else:
                summary = "AI had an existential crisis and refused to work."
            return {
                "score": 0.0,
                "summary": summary,
            }


gemini_service = GeminiService()
