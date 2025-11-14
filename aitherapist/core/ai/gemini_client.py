# core/ai/gemini_client.py
"""
Google Gemini API Client for AI Therapist Response Generation
"""

import os
import logging
from pathlib import Path
import google.generativeai as genai   #correct import

logger = logging.getLogger(__name__)

API_KEY_FILE = (
    Path(__file__)
    .resolve()
    .parent.parent.parent.parent
    / "gemini_api_key.txt"
)


def get_gemini_response(user_message: str) -> str:
    """
    Generate an empathetic response using Google Gemini API (1.5 Flash).
    """

    #Load API key (file first, then env)
    api_key = None

    if API_KEY_FILE.exists():
        try:
            with open(API_KEY_FILE, "r") as f:
                api_key = f.read().strip()
        except Exception as e:
            logger.warning(f"Could not read API key from file: {e}")

    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found. Add gemini_api_key.txt or set environment variable."
        )

    try:
        #Configure Gemini API (v1, correct)
        genai.configure(api_key=api_key)

        #Correct and available model (what you're allowed to use free)
        model = genai.GenerativeModel("gemini-1.5-flash")

        logger.info("Using Gemini model: gemini-1.5-flash")

        prompt = f"""
You are a compassionate, supportive AI therapist. 
Respond warmly and empathetically in 2–4 sentences.

User message: {user_message}

Your response:
        """

        #generate content using the correct method
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 400,
            }
        )

        return response.text.strip()

    except Exception as e:
        logger.error(f"Gemini API error: {e}")

        return (
            "I'm here with you. I'm having a technical issue responding fully right now, "
            "but you're not alone. You can share more if you'd like."
        )
