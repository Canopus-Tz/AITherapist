# How to Set GEMINI_API_KEY on Windows

## Step 1: Get Your API Key
1. Go to: https://aistudio.google.com/apikey
2. Sign in with your Google account
3. Click "Create API Key" or use an existing key
4. Copy the API key (it will look like: `AIzaSy...`)

## Step 2: Set Environment Variable

### Method 1: Windows System Settings (Permanent - Recommended)

1. **Open System Properties:**
   - Press `Win + R`
   - Type: `sysdm.cpl` and press Enter
   - OR: Right-click "This PC" → Properties → Advanced system settings

2. **Set Environment Variable:**
   - Click "Environment Variables" button
   - Under "User variables" (or "System variables"), click "New"
   - Variable name: `GEMINI_API_KEY`
   - Variable value: `your-api-key-here` (paste your actual key)
   - Click OK on all dialogs

3. **Restart your terminal/IDE** for changes to take effect

### Method 2: PowerShell (Temporary - Current Session Only)

Open PowerShell and run:
```powershell
$env:GEMINI_API_KEY="your-api-key-here"
```

**Note:** This only works for the current PowerShell session. Close and reopen = gone.

### Method 3: Command Prompt (Temporary - Current Session Only)

Open CMD and run:
```cmd
set GEMINI_API_KEY=your-api-key-here
```

**Note:** This only works for the current CMD session.

### Method 4: Set in Your IDE (VS Code, PyCharm, etc.)

**VS Code:**
- Open `.vscode/launch.json` or create it
- Add to "env" section:
```json
{
    "env": {
        "GEMINI_API_KEY": "your-api-key-here"
    }
}
```

**PyCharm:**
- Run → Edit Configurations
- Environment variables → Add `GEMINI_API_KEY=your-api-key-here`

## Step 3: Verify It's Set

Open PowerShell/CMD and run:
```powershell
echo $env:GEMINI_API_KEY
```

Or in CMD:
```cmd
echo %GEMINI_API_KEY%
```

You should see your API key printed.

## Step 4: Test Your Django App

Run your Django server:
```bash
python manage.py runserver
```

Try sending a chat message. If you see an error about missing API key, the environment variable isn't set correctly.

## Troubleshooting

- **"GEMINI_API_KEY environment variable is not set"**
  - Make sure you restarted your terminal/IDE after setting the variable
  - Verify with `echo $env:GEMINI_API_KEY` (PowerShell) or `echo %GEMINI_API_KEY%` (CMD)
  - If using Method 1, make sure you set it as a User variable (not System)

- **API key not working**
  - Make sure you copied the entire key (it's long)
  - Check that there are no extra spaces
  - Verify the key is active in Google AI Studio

