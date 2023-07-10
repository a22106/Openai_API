import os
import openai
from dotenv import load_dotenv
from argparse import ArgumentParser
from datetime import datetime

# Current file path
current_path = os.path.dirname(os.path.abspath(__file__))
models = {3: "gpt-3.5-turbo", 4: "gpt-4"}
presets ={
  "0": """You are an AI Programming assistant.
  
  - Follow the user's requirements carefully & to the letter.
  - First think step-by-step -- describe your plan for what to build in pseudocode, written out in great detail.
  - Then output the code in a single code block.
  - Minimize any other prose.
  """,
  "1": "You are an English teacher. The teacher is helpful, creative, clever, and very friendly. Fix the sentences enclosed in quotes.",
  "2": "You are a software engineer. The engineer is helpful, creative, clever, and very friendly.",
  
  # Translator from Chinese to English
  "3": """You are a Translator. 
  
  - Translate the following Chinese sentence enclosed in quotes into English.
  - The translation should be grammatically correct and natural.
  - The translation should be as short as possible. 
  - Don't add a comma after the word "because".
  
  """,
  "4": """I want you to act as a translator that translates the following words or sentences to Vietnamese.
  The translation should be grammatically correct and natural. The translation can be polished to be more natural.
  """,
  
  "translator": """I want you to act as a translator that translates the following words or sentences to LANG. Make sure the translation is grammatically correct and natural. Make the sentences as short as possible.
  """
}

parser = ArgumentParser()
parser.add_argument("--prompt", "-pp", type=str, default=presets["0"], help="Prompt of ChatGPT")
parser.add_argument("--preset", "-ps", type=str, help="Prompt preset of ChatGPT", default="0")
parser.add_argument("--show_presets", "-sp", action="store_true", help="Show presets of ChatGPT")
parser.add_argument("--model", "-m", type=int, default=4, help="Model of ChatGPT")
args = parser.parse_args()

# Load .env file
load_dotenv()
MODEL = models[args.model]
API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = API_KEY
END_MESSAGE = ["END", "EXIT"]


# Log feature start
SERVER_START = datetime.now().strftime('%Y%m%d_%H%M%S')
def print_message(*args):
    with open(f'{current_path}/logs/ChatGPTLog_{SERVER_START}.txt', 'a') as log_file:
        for arg in args:
            if type(arg) == list or type(arg) == tuple:
                for item in arg:
                    now = current_time()
                    log_file.write(str(now) + ': ' + str(item) + '\n')
                    print(str(now) + ': ' + str(item))
            
            elif type(arg) == dict:
                for key in arg:
                    now = current_time()
                    
                    log_file.write(str(now) + ': ' + str(key) + ': ' + str(arg[key]) + '\n')
                    print(str(now) + ': ' + str(key) + ': ' + str(arg[key]))
            else:   
                now = current_time()
                     
                log_file.write(str(now) + ': ' + str(arg) + '\n')
                print(str(now) + ': ' + str(arg))
                

if not os.path.exists(f'{current_path}/logs'):
        os.mkdir(f'{current_path}/logs')

def current_time():
    now = datetime.now().strftime('%y-%m-%d %H:%M:%S')
    return now
# Log feature end

# Get value index of presets
print_message("Preset: " + args.preset)
try:
  if args.preset in presets:
    if args.preset == "translator":
      print_message("Which language do you want to translate to?")
      print_message("1. English")
      print_message("2. Custom")
      lang = input("User: ")
      if lang == "1":
        lang = "English"
      elif lang == "2":
        lang = input("User: ")
      args.prompt = presets[args.preset].replace('LANG', lang)
    else:
      args.prompt = presets[args.preset]
except:
  pass
messages = [{"role": "system", "content": args.prompt}]

def interact_with_ChatGPT():
  global messages
  replies = []
  print_message(f"###################################################################################")
  print_message(f"WELCOME TO PIUS' CHATGPT")
  print_message(f"This program is powered by OpenAI's ChatGPT API")
  print_message(f"When you are done chatting, please type '{END_MESSAGE}' to end the chat. Thank you!")
  print_message(f"ChatGPT Model: {MODEL}")
  print_message(f"###################################################################################\n\n")
  print_message(f"PROMPT: {args.prompt}")
  
  while True:
    try:
      user_text = input("User: ")
      print_message('User: ' + user_text)
      
      if user_text in END_MESSAGE:
        print_message("ChatGPT: Bye bye!")
        break
      
      messages.append({"role": "user", "content": user_text})
      response = openai.ChatCompletion.create(model=MODEL, messages=messages)
      reply = response.choices[0].message.content
      print_message("ChatGPT: " + reply)
      messages.append({"role": "assistant", "content":reply})
    except openai.error.RateLimitError:
      print_message("OpenAI Error: (RateLimitError)API rate limit reached. Please wait a few minutes before trying again.")
      continue


if __name__ == "__main__":
  
  if args.show_presets:
    for preset, prompt in presets.items():
      print(f"{preset}: {prompt}")
    exit()

  # Run the chatbot
  if args.prompt:
    # Start log 
    print_message('Server start time: ', SERVER_START)
    interact_with_ChatGPT()