import os
import openai
from dotenv import load_dotenv
from argparse import ArgumentParser
from datetime import datetime

# Current file path
current_path = os.path.dirname(os.path.abspath(__file__))
presets ={
  0: """You are an AI Programming assistant.
  
  - Follow the user's requirements carefully & to the letter.
  - First think step-by-step -- describe your plan for what to build in pseudocode, written out in great detail.
  - Then output the code in a single code block.
  - Minimize any other prose.
  """,
  1: "You are an English teacher. The teacher is helpful, creative, clever, and very friendly. Fix the sentences enclosed in quotes.",
  2: "You are a software engineer. The engineer is helpful, creative, clever, and very friendly.",
  
  # Translator from Chinese to English
  3: """You are a Translator. 
  
  - Translate the following Chinese sentence enclosed in quotes into English.
  - The translation should be grammatically correct and natural.
  - The translation should be as short as possible. 
  - Don't add a comma after the word "because".
  
  """
}

parser = ArgumentParser()
parser.add_argument("--prompt", "-pp", type=str, default=presets[0], help="Prompt of ChatGPT")
parser.add_argument("--preset", "-ps", type=int, help="Prompt preset of ChatGPT", default=0)
parser.add_argument("--show_presets", "-sp", action="store_true", help="Show presets of ChatGPT")
args = parser.parse_args()

# Load .env file
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = API_KEY

# Get value index of presets
try:
  if args.preset in presets:
    args.prompt = presets[args.preset]
except:
  pass
messages = [{"role": "system", "content": args.prompt}]

def interact_with_ChatGPT():
  global messages
  replies = []
  
  print_message(f"PROMPT: {args.prompt}")
  
  while True:
    try:
      user_text = input("User: ")
      print_message('User: ' + user_text)
      messages.append({"role": "user", "content": user_text})
      response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
      reply = response.choices[0].message.content
      print_message("ChatGPT: " + reply)
      messages.append({"role": "assistant", "content":reply})
      if "Thank you for your time" in reply or "Thank you" in user_text:
        break
    except openai.error.RateLimitError:
      print_message("OpenAI Error: (RateLimitError)API rate limit reached. Please wait a few minutes before trying again.")
      continue
  

# Log feature start
SERVER_START = datetime.now().strftime('%Y%m%d_%H%M%S')

if not os.path.exists(f'{current_path}/logs'):
        os.mkdir(f'{current_path}/logs')

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

def current_time():
    now = datetime.now().strftime('%y-%m-%d %H:%M:%S')
    return now
# Log feature end


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