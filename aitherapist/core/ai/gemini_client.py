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
You are a compassionate, supportive AI therapist. 
Respond warmly and empathetically in 2–4 sentences. Do not leave a question un-responded always respond, for something that
you have no response to you can respond with "i am not aware of this at the moment. "

User message: {user_message}

Your response:
        """

        # Generate content using the correct method
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 400,
            }
        )
        
        #Check for text attribute
        if response.text:
            return response.text.strip()
        
        # 2. Check for generation blocking or incomplete status
        if not response.candidates:
            # Check if prompt feedback gives a reason for blocking the input itself
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                 block_reason = response.prompt_feedback.block_reason.name
                 raise RuntimeError(f"Prompt blocked by API safety settings: {block_reason}")
            # If no candidates and no prompt feedback, it's an unexpected error
            raise RuntimeError("Model returned no candidates (generation failed or blocked).")

        # Get the first candidate's finish reason
        candidate = response.candidates[0]
        finish_reason = candidate.finish_reason
        
        # Check if generation was stopped prematurely (not by completing the response)
        if finish_reason != genai.types.FinishReason.STOP:
            # Content was blocked by safety filter
            if finish_reason == genai.types.FinishReason.SAFETY:
                safety_ratings = candidate.safety_ratings
                raise RuntimeError(f"Response blocked due to safety settings: {safety_ratings}")
            
            # Content was truncated (max_output_tokens reached)
            elif finish_reason == genai.types.FinishReason.MAX_OUTPUT_TOKENS:
                # Still try to return the partial text if available
                if response.text:
                    return response.text.strip()
                raise RuntimeError("Generation stopped: Maximum output tokens reached.")
            
            # Other block reasons (e.g., RECITATION, OTHER)
            else:
                 raise RuntimeError(f"Generation stopped prematurely. Finish Reason: {finish_reason.name}")

        # If we reach here, the response.text was empty for an otherwise successful STOP finish reason.
        # This is highly unlikely with a STOP, but we maintain the explicit fail:
        raise RuntimeError("No text returned from model response, even though Finish Reason was STOP.")

        # --- END OF IMPROVED RESPONSE EXTRACTION ---

    except Exception as e:
        # Your existing robust error handling block is excellent and will catch the 
        # RuntimeError from above, report the error, and provide the model suggestions.
        err_text = str(e)
        logger.error(f"Gemini API error: {err_text}")

        suggestion = ""
        try:
            # Try to list available models if the library exposes that API
            if hasattr(genai, "list_models"):
                models = genai.list_models()
                ids = []
                # Filter out models to keep the error message clean
                for m in models:
                    name = getattr(m, "name", str(m))
                    # Only show models used for generation (not just embeddings, etc.)
                    if "generateContent" in getattr(m, "supported_generation_methods", []):
                        # Extract just the ID, e.g., 'gemini-2.5-flash' from 'models/gemini-2.5-flash'
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