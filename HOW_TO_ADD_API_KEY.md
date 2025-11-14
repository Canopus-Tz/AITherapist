# How to Add Your Gemini API Key

## Option 1: Using a Local File (Easiest - Recommended)

1. **Get your API key:**
   - Go to: https://aistudio.google.com/apikey
   - Sign in and create/copy your API key

2. **Create the API key file:**
   - In the project root folder (same level as `requirements.txt`), create a file named: `gemini_api_key.txt`
   - Open it and paste ONLY your API key (no quotes, no extra text)
   - Save the file

   Example file content:
   ```
   AIzaSyYourActualApiKeyHere123456789
   ```

3. **That's it!** The system will automatically read from this file.

## Option 2: Environment Variable (Alternative)

If you prefer using environment variables, you can still set `GEMINI_API_KEY` as an environment variable. The system will try the file first, then fall back to the environment variable.

## Security Note

The `gemini_api_key.txt` file is automatically ignored by Git (added to `.gitignore`), so it won't be committed to your repository. This keeps your API key safe!

## Verify It Works

1. Make sure `gemini_api_key.txt` exists in the project root
2. Run your Django server: `python manage.py runserver`
3. Try sending a chat message
4. If you see an error, check that:
   - The file is named exactly `gemini_api_key.txt`
   - The file is in the project root (same folder as `requirements.txt`)
   - The API key is on a single line with no extra spaces

