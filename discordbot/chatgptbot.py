import os
import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle, Select, SelectOption
import openai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = API_KEY

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='@pius_chatgpt ', intents=intents)

presets = {
    0: "You are an AI Programming assistant.",
    1: "You are an English teacher. The teacher is helpful, creative, clever, and very friendly. Fix the sentences enclosed in quotes.",
    2: "You are a software engineer. The engineer is helpful, creative, clever, and very friendly.",
}

messages = []

async def interact_with_ChatGPT(user_text):
    global messages
    messages.append({"role": "user", "content": user_text})
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    return reply

@bot.event
async def on_ready():
  print(f'{bot.user} has connected to Discord!')
  DiscordComponents(bot)

@bot.command(name='start')
async def start(ctx):
  options = [SelectOption(label=f"Preset {i}", value=str(i), description=presets[i][:97]) for i in presets]
  select = Select(placeholder="Select a preset", min_values=1, max_values=1, options=options)
  await ctx.send("Choose a preset to start the conversation:", components=[select])

@bot.event
async def on_component(ctx):
  if isinstance(ctx.component, Select):
    selected_preset = int(ctx.selected_options[0])
    global messages
    messages = [{"role": "system", "content": presets[selected_preset]}]
    await ctx.send(f"Selected preset: {presets[selected_preset]}", components=[])

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  if not message.content.startswith("@pius_chatgpt"):
    user_text = message.content
    reply= await interact_with_ChatGPT(user_text)
  await message.channel.send(reply)
  await bot.process_commands(message)
  
if __name__ == "__main__":
  bot.run(DISCORD_TOKEN)
