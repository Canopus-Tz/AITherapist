# core/ai/gemini_client.py
"""
Google Gemini API Client for AI Therapist Response Generation
"""

import os
import logging
from pathlib import Path
import google.generativeai as genai 

logger = logging.getLogger(__name__)

API_KEY_FILE = (
    Path(__file__)
    .resolve()
    .parent.parent.parent.parent
    / "gemini_api_key.txt"
)

MODEL_FILE = (
    Path(__file__)
    .resolve()
    .parent.parent.parent.parent
    / "gemini_model.txt"
)

def get_gemini_response(user_message: str) -> str:
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
        # Configure Gemini API
        genai.configure(api_key=api_key)

        # Determine model: file -> env -> default
        model_name = None
        if MODEL_FILE.exists():
            try:
                with open(MODEL_FILE, "r") as f:
                    model_name = f.read().strip()
            except Exception as e:
                logger.warning(f"Could not read model from file: {e}")

        if not model_name:
            model_name = os.getenv("GEMINI_MODEL")

        # Set the default to a stable, supported model
        if not model_name:
            model_name = "gemini-2.5-flash"

        logger.info(f"Using Gemini model: {model_name}")

        model = genai.GenerativeModel(model_name)

        prompt = f"""
You are a supportive AI therapy assistant called AItherapist.

Your role is to help users explore their thoughts and emotions in a calm,
empathetic, and non-judgmental way. You listen actively, validate feelings,
and guide reflection through gentle, open-ended questions.

You should follow an emotion-aware flow:
• Help users describe how intense a feeling is
• Explore whether the feeling is recurring or recent
• Gently ask about patterns, triggers, or changes over time

You must NOT behave like a question-only chatbot.
Balance reflective questions with supportive guidance, grounding suggestions,
and practical emotional coping strategies when appropriate.

You may offer gentle advice such as:
• breathing or grounding exercises
• journaling or self-reflection
• small, manageable steps for emotional relief

You do NOT provide medical or psychiatric diagnoses.
You do NOT prescribe medication.
You do NOT replace professional therapists.

If a user asks unrelated or general questions, gently redirect the conversation
back to emotional well-being and mental health support.

Your tone must always be:
• empathetic
• calm
• supportive
• human-like
• non-judgmental

Your goal is emotional support and self-awareness, not factual Q&A.

Always refer yourself as AItherapist.

FORMAT YOUR RESPONSES USING THE FOLLOWING RULES:

1. Always separate ideas into medium sized paragraphs.
   - Never write a single large block of text.
   - Use line breaks to create visual breathing space.

2. Structure responses in this order when appropriate:
   a) Emotional reflection (3-4 sentences)
   b) Gentle exploration (at most One question)
   c) Supportive guidance (optional)
   d) Warm, open-ended closing

3. Use emphasis sparingly:
   - Bold ONLY emotional reflections or key validating phrases.
   - Do NOT overuse bold or italics.

4. Emojis:
   - Emojis are optional.
   - Use at most ONE emoji per response.
   - Emojis must be calm and supportive (e.g. 🌱 💙 🌤️ and other supportive emojis).
   - Never use emojis that are playful, exaggerated, or distracting.

5. Tone and pacing:
   - Write as a calm therapist, not a chatbot.
   - Allow pauses through spacing, not filler words.
   - Avoid lists unless they improve clarity.

6. Do NOT:
   - Use bullet points excessively
   - Ask multiple questions at once
   - Use emojis in serious or high-distress moments

SAFETY & BOUNDARY RULES:

- Remember you are a supportive conversational assistant, not a therapist or medical professional.
- If you sense any user distress escalation or persistance at a high level, shift from exploration to support and safety.
- Reduce questions when emotional intensity is high.
- Do not attempt to diagnose, solve, or interpret deeply in high-risk situations.
- Encourage seeking support from trusted people or professionals when appropriate.
- Never present yourself as the only source of help.
- Maintain calm, respectful, non-alarming language at all times.
- It is not a must to start with "hello there" on every response that comes from you.

NB: at the end of each chat remember to finish with a short summary of what you have discussed with the user and solutions that
you have offered.

User message: {user_message}

Your response:
        """

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 2048, 
            }
        )
        
        full_response = _extract_full_response(response)
        return full_response

    except Exception as e:
        err_text = str(e)
        logger.error(f"Gemini API error: {err_text}")

        suggestion = ""
        try:
            if hasattr(genai, "list_models"):
                models = genai.list_models()
                ids = []
                for m in models:
                    name = getattr(m, "name", str(m))
                    if "generateContent" in getattr(m, "supported_generation_methods", []):
                        ids.append(name.replace("models/", ""))
                
                #set of stable models for the suggestion list
                stable_ids = [
                    "gemini-2.5-flash", 
                    "gemini-2.5-pro", 
                    "gemini-flash-latest", 
                    "gemini-pro-latest"
                ]
                
                # Show only the stable IDs for simplicity
                suggestion_list = [id for id in stable_ids if id in ids] or ids[:4]
                
                if suggestion_list:
                    suggestion = (
                        "Available stable models: " + ", ".join(suggestion_list) + ". "
                        "Set the environment variable `GEMINI_MODEL` or create a `gemini_model.txt` "
                        "file with a supported model name."
                    )
        except Exception:
            # If listing models failed, include a generic hint
            suggestion = (
                "If you see a 'model not found' error, ensure you are using a supported "
                "model name (e.g., 'gemini-2.5-flash')."
            )

        user_message = (
            "I'm here with you. I'm having a technical issue responding fully right now, "
            "but you're not alone. You can share more if you'd like.\n\n"
            "Technical note: " + err_text + "\n" + suggestion
        )

        return user_message


def _extract_full_response(response) -> str:
    # Case 1: Check for text attribute (normal successful case)
    if response.text:
        return response.text.strip()
    
    # Case 2: Check for generation blocking or incomplete status
    if not response.candidates:
        # Check if prompt feedback gives a reason for blocking the input itself
        if response.prompt_feedback and response.prompt_feedback.block_reason:
             block_reason = response.prompt_feedback.block_reason.name
             raise RuntimeError(f"Prompt blocked by API safety settings: {block_reason}")
        # If no candidates and no prompt feedback, it's an unexpected error
        raise RuntimeError("Model returned no candidates (generation failed or blocked).")

    # Case 3: Get the first candidate and check finish reason
    candidate = response.candidates[0]
    finish_reason = candidate.finish_reason
    
    # Case 3a: Normal completion (STOP reason)
    if finish_reason == genai.types.FinishReason.STOP:
        if response.text:
            return response.text.strip()
        else:
            raise RuntimeError("No text returned despite STOP finish reason.")
    
    # Case 3b: Blocked by safety filter
    elif finish_reason == genai.types.FinishReason.SAFETY:
        safety_ratings = candidate.safety_ratings
        raise RuntimeError(f"Response blocked due to safety settings: {safety_ratings}")
    
    # Case 3c: Truncated due to max_output_tokens
    elif finish_reason == genai.types.FinishReason.MAX_OUTPUT_TOKENS:
        if response.text:
            logger.warning(
                f"Response was truncated at max_output_tokens limit. "
                f"Returning partial response ({len(response.text)} chars). "
                f"Consider increasing max_output_tokens or enabling streaming."
            )
            return response.text.strip()
        raise RuntimeError("Generation stopped: Maximum output tokens reached (no text available).")
    
    # Case 3d: Other block reasons (RECITATION, OTHER, etc.)
    else:
         raise RuntimeError(f"Generation stopped prematurely. Finish Reason: {finish_reason.name}")