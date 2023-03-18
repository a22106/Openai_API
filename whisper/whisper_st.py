import stable_whisper
import os
import json
from tools.utils import utils
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('--model', type=str, default='large', help='Model to use. Can be "tiny", "tiny.en", "base", "base.en", "small", "small.en", "medium", "medium.en", "large"')

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        # watching files end with .mp3, .webm
        if not event.is_directory and event.src_path.endswith('.mp3') or event.src_path.endswith('.webm'):
            print(f"New file added: {event.src_path}")
            time.sleep(1)  # Allow a short delay for the file to be fully written
            result = model.transcribe(event.src_path, verbose=True, word_timestamps=False)
            # print(result)

print("Loading model...")
start_time = time.time()
model = stable_whisper.load_model('large')
end_time = time.time()
time_elapsed = end_time - start_time
print(f"Model loaded. Took {time_elapsed:.2f} seconds to load.")

target_dir = '/home/bk22106/pius/github/Openai_API/whisper/whisper_audio'

if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=target_dir, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
