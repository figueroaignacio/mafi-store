import json
import time

from groq import Groq

from spite.core.config import get_settings

settings = get_settings()

ANALYSIS_PROMPT = """
You are reviewing a job posting. The user is specifically searching for: "{query}".

Analyze this job description and summarize what they are actually asking for,
including tech stack, responsibilities, and any other notable details.
Be concise and insightful. No corporate speak.

Title: {title}
Company: {company}
Location: {location}
Salary: {salary}
Description: {description}

Respond ONLY with valid JSON exactly matching this format:
{{
    "summary": "<concise summary of the role and what is asked>",
    "reasoning": "<any detailed reasoning, tech stack, responsibilities>",
    "red_flags": ["<flag1>", "<flag2>"],
    "green_flags": ["<flag1>", "<flag2>"]
}}
"""


class GroqService:
    def __init__(self) -> None:
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = "llama-3.3-70b-versatile"

    def analyze_job(
        self,
        query: str,
        title: str,
        company: str,
        description: str,
        location: str | None = None,
        salary: str | None = None,
    ) -> dict:
        prompt = ANALYSIS_PROMPT.format(
            query=query,
            title=title,
            company=company,
            location=location or "Not specified",
            salary=salary or "Not disclosed",
            description=description or "No description provided.",
        )

        max_retries = 3
        base_delay = 10

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model=self.model,
                )
                raw = response.choices[0].message.content.strip()
                if raw.startswith("```"):
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                result = json.loads(raw)
                return result

            except json.JSONDecodeError:
                return {"summary": "Could not parse AI response."}
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "rate_limit" in error_str.lower():
                    if attempt < max_retries - 1:
                        time.sleep(base_delay * (2**attempt))
                        continue
                    else:
                        summary = "Rate limit hit — AI is taking a break. Try again in a minute."
                elif "API_KEY" in error_str or "401" in error_str:
                    summary = "Invalid API key."
                    break
                else:
                    summary = "AI analysis failed."
                    break

        return {"summary": summary}


groq_service = GroqService()
