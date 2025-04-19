# import discord
# from discord.ext import commands
# from google import genai
# from google.genai import types
# from google.genai.types import GenerateContentConfig, GoogleSearch, Tool

# import os
# import logging
# from dotenv import load_dotenv
# import asyncio

# # --- Configuration ---
# load_dotenv()

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# if not GEMINI_API_KEY:
#     raise RuntimeError("GEMINI_API_KEY not set in .env!")

# # Initialize the Gemini API client with the API key
# client = genai.Client(api_key=GEMINI_API_KEY)

# MODEL = "gemini-2.0-flash"

# DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
# if not DISCORD_TOKEN:
#     print("Missing DISCORD_BOT_TOKEN in .env file.")
#     exit()

# # --- Logging Setup ---
# logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
# logger = logging.getLogger('discord')

# # --- Discord Bot Setup ---
# intents = discord.Intents.default()
# intents.messages = True
# intents.message_content = True

# bot = commands.Bot(command_prefix='!', intents=intents)

# @bot.event
# async def on_ready():
#     print(f"Logged in as {bot.user} (ID: {bot.user.id})")
#     await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="!check statements"))

# @bot.command(name='check', help='Fact-checks a statement using Gemini + Google Search.')
# async def check_fact(ctx, *, statement: str):
#     thinking_msg = await ctx.reply(f"⏳ Checking the statement: \"{statement[:100]}...\"")

#     prompt_text = f"""
#     Please act as a fact-checker. Evaluate the factual accuracy of the following statement, using Google Search if needed.

#     Statement: "{statement}"

#     Give a short, clear evaluation (e.g. Accurate, Inaccurate, Misleading, Unverifiable) with a concise reason.
#     """

#     try:
#         google_search_tool = Tool(google_search=GoogleSearch())
#         content = [genai.types.Content(role="user", parts=[genai.types.Part.from_text(text=prompt_text)])]

#         response = await asyncio.to_thread(
#             client.models.generate_content,
#             model=MODEL,
#             config=GenerateContentConfig(
#                 temperature=0.7,
#                 top_p=1.0,
#                 top_k=1,
#                 max_output_tokens=512,
#                 tools=[google_search_tool],
#                 response_modalities=["TEXT"],
#                 system_instruction=prompt_text
#             ),
#             contents=content
#         )

#         if hasattr(response, 'text') and response.text:
#             result_text = response.text
#             reply_content = f"🔍 **Fact-Check Result:** \"{statement}\"\n\n{result_text}"
#             if len(reply_content) > 2000:
#                 reply_content = reply_content[:1990] + "... (truncated)"
#             await thinking_msg.edit(content=reply_content)
#         else:
#             await thinking_msg.edit(content="⚠️ I couldn't generate a response. Try again.")

#     except Exception as e:
#         logger.error("Error in Gemini response:", exc_info=True)
#         await thinking_msg.edit(content=f"⚠️ Something went wrong: {str(e)[:300]}")

# @bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.CommandNotFound):
#         return  # Silently ignore unknown commands

#     elif isinstance(error, commands.MissingRequiredArgument):
#         await ctx.reply("❗ Missing argument. Usage: `!check <statement>`")

#     elif isinstance(error, commands.CommandInvokeError):
#         original = error.original
#         logger.error(f"Command invoke error: {original}", exc_info=True)

#         if isinstance(original, discord.HTTPException):
#             await ctx.reply("⚠️ Discord API error. Please try again.")
#         elif isinstance(original, asyncio.TimeoutError):
#             await ctx.reply("⏱️ Operation timed out. Please try again.")
#         else:
#             await ctx.reply(f"⚠️ An error occurred: {str(original)}")

#     else:
#         logger.error(f"Unexpected error: {error}", exc_info=True)
#         await ctx.reply("❌ Unexpected error occurred. Please try again later.")

# # --- Run Bot ---
# if __name__ == "__main__":
#     try:
#         bot.run(DISCORD_TOKEN)
#     except discord.errors.LoginFailure:
#         print("Invalid Discord token.")

import discord
from discord.ext import commands
from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig, GoogleSearch, Tool

import os
import logging
from dotenv import load_dotenv
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import threading
import uvicorn

# --- Configuration ---
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in .env!")

# Initialize the Gemini API client with the API key
client = genai.Client(api_key=GEMINI_API_KEY)

MODEL = "gemini-2.0-flash"

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not DISCORD_TOKEN:
    print("Missing DISCORD_BOT_TOKEN in .env file.")
    exit()

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger('discord')


# --- FastAPI Setup ---
app = FastAPI()

class FactCheckRequest(BaseModel):
    statement: str

@app.get("/")
async def root():
    return {"Status": "Active"}

@app.post("/check/")
async def check_fact(request: FactCheckRequest):
    statement = request.statement

    # --- Google Search Tool Setup ---
    prompt_text = f"""
    Please act as a fact-checker. Evaluate the factual accuracy of the following statement, using Google Search if needed.

    Statement: "{statement}"

    Give a short, clear evaluation (e.g. Accurate, Inaccurate, Misleading, Unverifiable) with a concise reason.
    """

    try:
        google_search_tool = Tool(google_search=GoogleSearch())
        content = [genai.types.Content(role="user", parts=[genai.types.Part.from_text(text=prompt_text)])]

        # Generate content using Gemini model
        response = await asyncio.to_thread(client.models.generate_content, 
            model=MODEL,
            config=GenerateContentConfig(
                temperature=0.7,
                top_p=1.0,
                top_k=1,
                max_output_tokens=512,
                tools=[google_search_tool],
                response_modalities=["TEXT"],
                system_instruction=prompt_text  # Integrating Google Search tool
            ),
            contents=content  # Pass the correct content here
        )

        # Check the response for the text and send the reply
        if hasattr(response, 'text') and response.text:
            result_text = response.text
            return {
                "statement": statement,
                "result": result_text
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate response.")

    except Exception as e:
        logger.error(f"Error during Gemini API call or processing: {e}")
        raise HTTPException(status_code=500, detail=f"Error while checking the statement: `{e}`")


# --- Discord Bot Setup ---
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="!check statements"))

@bot.command(name='check', help='Fact-checks a statement using Gemini + Google Search.')
async def check_fact_discord(ctx, *, statement: str):
    # --- Google Search Tool Setup ---
    thinking_msg = await ctx.reply(f"⏳ Checking the statement: \"{statement[:100]}...\"")

    # Use the pre-initialized client to generate content
    prompt_text = f"""
    Please act as a fact-checker. Evaluate the factual accuracy of the following statement, using Google Search if needed.

    Statement: "{statement}"

    Give a short, clear evaluation (e.g. Accurate, Inaccurate, Misleading, Unverifiable) with a concise reason.
    """

    try:
        google_search_tool = Tool(google_search=GoogleSearch())
        content = [genai.types.Content(role="user", parts=[genai.types.Part.from_text(text=prompt_text)])]

        # Generate content using Gemini model
        response = await asyncio.to_thread(client.models.generate_content, 
            model=MODEL,
            config=GenerateContentConfig(
                temperature=0.7,
                top_p=1.0,
                top_k=1,
                max_output_tokens=512,
                tools=[google_search_tool],
                response_modalities=["TEXT"],
                system_instruction=prompt_text  # Integrating Google Search tool
            ),
            contents=content  # Pass the correct content here
        )

        # Check the response for the text and send the reply
        if hasattr(response, 'text') and response.text:
            result_text = response.text
            reply_content = f"🔍 **Fact-Check Result:** \"{statement}\"\n\n{result_text}"
            if len(reply_content) > 2000:
                reply_content = reply_content[:1990] + "... (truncated)"
            await thinking_msg.edit(content=reply_content)
        else:
            await thinking_msg.edit(content="I couldn't generate a response. Try again.")

    except Exception as e:
        logger.error(f"Error during Gemini API call or processing: {e}")
        await thinking_msg.edit(content=f"Error while checking the statement: `{e}`")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f"Missing argument. Usage: `!check <statement>`")
    elif isinstance(error, commands.CommandInvokeError):
        logger.error(f"Error invoking command {ctx.command.name}: {error.original}")
        await ctx.reply("Internal error occurred.")
    else:
        logger.error(f"Unhandled error: {error}")
        await ctx.reply("Unexpected error occurred.")

# --- Running both Discord Bot and FastAPI Server ---
def run_discord_bot():
    try:
        bot.run(DISCORD_TOKEN)
    except discord.errors.LoginFailure:
        print("Invalid Discord token.")

if __name__ == "__main__":
    # Running FastAPI using Uvicorn in a separate thread
    threading.Thread(target=uvicorn.run, args=("main:app",), daemon=True).start()

    # Running Discord Bot
    run_discord_bot()
