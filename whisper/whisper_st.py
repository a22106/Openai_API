import os
import time
from argparse import ArgumentParser
from datetime import datetime
import json

import stable_whisper
from tools.utils import utils
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

CUR_PATH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PATH = os.path.join(CUR_PATH, 'input')
OUTPUT_PATH = os.path.join(CUR_PATH, 'output')

parser = ArgumentParser()
parser.add_argument('--model', '-m', type=str, default='large', help='Model to use. Can be "tiny", "tiny.en", "base", "base.en", "small", "small.en", "medium", "medium.en", "large"')
parser.add_argument('--watch', '-w', type=str, default=DEFAULT_PATH, help='Watch a directory for new files(.mp3, ) and transcribe them')
parser.add_argument('--input', '-i', type=str, default=DEFAULT_PATH, help='Input file path to transcribe')
parser.add_argument('--output', '-o', type=str, default=OUTPUT_PATH, help='Output file path to save the transcription')
parser.add_argument('--sleep', '-s', action='store_true', default=False, help='Sleep for each segment', required=False)
parser.add_argument('--save', '-S', type=str, default=None, help='Save the transcription to a file, "ass", "srt", or "json"')
parser.add_argument('--verbose', '-v', action='store_true', default=None, help='Print verbose output')
args = parser.parse_args()

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def delay_segment(text, start, end):
    delayed = end - start
    start_timestamp = datetime.utcfromtimestamp(start).strftime('%H:%M:%S')
    end_timestamp = datetime.utcfromtimestamp(end).strftime('%H:%M:%S')
    print(f"[{start_timestamp}] --> [{end_timestamp}]", end=' ')
    print(text)
    time.sleep(delayed)


def load_model(model_name):
    print("Loading model...")
    start_time = time.time()
    model = stable_whisper.load_model(model_name)
    end_time = time.time()
    time_elapsed = end_time - start_time
    print(f"Model loaded. Took {time_elapsed:.2f} seconds to load.")
    print("Waiting for new audio to play...")
    return model


class MyHandler(FileSystemEventHandler):
    AUDIO_EXTENSIONS = ('.mp3', '.webm', '.m4a', '.wav')
    TRANSCRIPTION_OPTIONS = {'language': 'english'}

    def __init__(self, args, model):
        self.args = args
        self.model = model
        self.verbose = args.verbose

    # when the file is created, it will be processed
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(MyHandler.AUDIO_EXTENSIONS):
            self.process_audio_file(event.src_path)

    def process_audio_file(self, file_path):
        filename = os.path.splitext(os.path.basename(file_path))[0]
        # print(f"New audio detected: {file_path}")
        time.sleep(1)  # Allow a short delay for the file to be fully written

        result = self.model.transcribe(file_path, verbose=self.verbose, word_timestamps=False, **MyHandler.TRANSCRIPTION_OPTIONS)

        if self.args.save:
            output_filename = os.path.join(args.output, f"{filename}.{self.args.save}")
            result_file = self.save_transcription(result, output_filename)
            if self.args.sleep:  # Sleep for each segment
                for i, segment in enumerate(result_file["ori_dict"]["segments"]):
                    start = result_file["ori_dict"]["segments"][i]["start"]
                    if i < len(result_file["ori_dict"]["segments"])-1:
                        start_next = result_file["ori_dict"]["segments"][i+1]["start"]
                    else:
                        start_next = result_file["ori_dict"]["segments"][i]["end"]
                    delay_segment(segment["text"], start, start_next)

    def save_transcription(self, result, output_path):
        if self.args.save == 'json':
            result.save_as_json(output_path)
        elif self.args.save == 'srt':
            result.to_srt_vtt(output_path)
        elif self.args.save == 'ass':
            result.to_ass(output_path)
        else:
            raise ValueError(f"Invalid save format: {self.args.save}")
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        return data


if __name__ == "__main__":
    model = load_model(args.model)
    
    mkdir(args.output) # Create output directory if it doesn't exist

    if args.watch:
        event_handler = MyHandler(args, model)
        observer = Observer()
        observer.schedule(event_handler, path=args.watch, recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
