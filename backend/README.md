# 🔍 Discord Fact-Checking Bot with Gemini API + Google Search

A powerful and intelligent Discord bot that verifies user-provided statements using Google Gemini 2.0 Flash model and Google Search tool.

> Built using Python, Discord.py, and Google Generative AI API.

---

##  Features

-  Uses **Gemini 2.0 Flash** model from Google.
-  Integrates **Google Search Tool** for fact-based grounding.
-  Evaluates user statements for **accuracy, misinformation, or unverifiability**.
- 📡 Responds directly inside Discord with clear, concise fact-check summaries.
- 🛠️ Handles errors, invalid tokens, and command misuse gracefully.

---

##  Tech Stack

- **Python 3.10+**
- [Discord.py](https://discordpy.readthedocs.io/)
- [Google Generative AI Python SDK](https://pypi.org/project/google-generativeai/)
- `dotenv` for loading secrets from `.env`

---

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo.git
   cd your-repo
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables in a `.env` file:
   ```env
    GEMINI_API_KEY=your_gemini_api_key
    DISCORD_BOT_TOKEN=your_discord_bot_token

   ```
5. Use this given below url to add bot to the server:
   ```
   https://discord.com/oauth2/authorize?client_id=1362787732442579004&permissions=1689934340025408&integration_type=0&scope=bot
   ```
6. Run the application:
   ```bash
   uv run main.py
   ```
## Usage
!check <your_statement>
