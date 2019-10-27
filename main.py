import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import json
import re
from tika import parser
import logging
import os.path as fs
import os

# TODO:
# - Add support for hot reloading ~/.file_move/file_move.json
#  - Add support more types

home = fs.expanduser("~")
file_move_json = home + "/.file_move/file-move.json"
log_file = home + "/.file_move/logs/app.log"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class MyHandler(FileSystemEventHandler):

     def match(self, path):
          # Look for the suffix of the path
          suffix = path.split('.')

          # List is empty. Return bc something is wrong with the path
          if not suffix:
               # TODO: Logging
               print("no suffix")
               logging.warning(f"No suffix found in file '{path}'. Something is wrong...")
               return
          # Get suffix of the path
          path_suffix = suffix[-1]

          # Open the file move rules and look for matching rules
          with open(file_move_json, 'r') as rules:
               # Load JSON data
               data = json.load(rules)
               print(f'Loaded rules from file {file_move_json} ...')
               for suf in data:
                    # print(suf)
                    # if path_suffix == suf:
                    if re.search(suf, path_suffix):
                         # See if anything matches
                         rule = self.contains(path, path_suffix, data[suf])
                         # If True -> found something
                         if rule:
                              dest = rule['destination']
                              print(f'Matched! Move file {path} to {dest}')
                              # shutil.move(path, dest)
                              self.move_file(path, dest)
                              return
                         else:
                              print("No match.")

     # Search in the given file if a contains-rule matches
     def contains(self, path, suffix, match):
          with open(path, 'r') as f:
               # If file is pdf
               if suffix == "pdf":
                    # Search in the pdf file
                    return self.pdfSearch(path, match)
               # If file is textbased
               # elif suffix in ["txt", "c", "java", "swift", "py", "json", "csv"]:
               elif re.search("(txt|c|java|swift|py|json|csv)", suffix):
                    # Search in the file
                    return self.txtSearch(path, match)
               else:
                    print("Something is wrong")


     # Search in pdf file
     def pdfSearch(self, path, match):
          # parse file
          raw = parser.from_file(path)
          # for each rule in the matching filetype
          for rule in match["rules"]:
               # See if any rules match
               for key in rule["contains-keyword"]:
                    # print(f'Search for {key}')

                    # Parse the regex rules with the text in the pdf
                    ResSearch = re.search(key, raw['content'])
                    if ResSearch:
                         # If a rule matches -> return
                         return rule

     # Search in text based files
     def txtSearch(self, path, match):
          with open(path, 'r') as f:
               # Load the content of the file
               data = f.read().replace('\n', '')
               for rule in match["rules"]:
                    # See if any rules match
                    for key in rule['contains-keyword']:
                         ResSearch = re.search(key, data)
                         if ResSearch:
                              # If a rule matches -> return
                              return rule

     # Move file to destination and log that move in app.log
     def move_file(self, source, dest):
          # Split parts of the file url
          path_parts = source.split("/")

          # In case path_parts is empty
          if not path_parts or len(path_parts) == 0:
               return
          # Get last path element
          file_name = path_parts[-1]

          # Check if the file already exists
          if not fs.exists(dest + '/' + file_name):
               # File doesn't exists yet -> file can be moved safely
               shutil.move(source, dest)
               # Log the move of the file
               logging.info(f'Moved file {source} to {dest}')
          # File already exists -> modify path
          else:
               ext = 1
               # Split file_name and file_suffix
               file_n, file_s = file_name.rsplit(".")

               # Generate filenames in format file_name(n).suff as long as they exist
               while fs.exists(dest + '/' + file_n + '(' + str(ext) + ').' + file_s):
                    ext += 1
               # Now the file name doesn't exist -> move file
               dest = dest + '/' + file_n + '(' + str(ext) + ').' + file_s
               # Move file
               shutil.move(source, dest)
               # Log file move
               logging.info(f'Moved file {source} to {dest}')

     def on_created(self, event):
          print(f'event type: {event.event_type}  path : {event.src_path}')
          self.match(str(event.src_path))

     def on_moved(self, event):
          print(f'event type: {event.event_type}  path : {event.src_path}')
          self.match(str(event.src_path))


def is_dir(path):
     return fs.isdir(path)

def is_file(path):
     return fs.exists(path)

# Creates dirs and files if "~/.file_move" not exists
def start_routine():
     if not is_dir(home + "/.file_move"):
          os.mkdir(home + "/.file_move")
     
     if not is_dir(home + "/.file_move/logs"):
          os.mkdir(home + "/.file_move/logs")

     if not is_file(file_move_json):
          with open(file_move_json, "w") as f:
               f.write("{\n\t\"observed-directories\": {\n\t\t\"dirs\": [\n\t\t\t\"Replace with the paths to the directories that should be observed.\"\n\t\t]\n\t},\n\t\n}")
          print(bcolors.WARNING + "Warning: Cd into ~/.file_move/file_move.json and add your observed directories." + bcolors.ENDC)

class ObserverHandler(FileSystemEventHandler): 

     observers = []



# Run this only if this file is the main file
if __name__ == "__main__":
     start_routine()
     # Config logging
     logging.basicConfig(filename=log_file, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
     # Create file Observer
     print("Running 'File Observer'")
     observers = []
     event_handler = MyHandler()

     # Add observer for all observing directories
     with open(file_move_json, 'r+') as f:
          data = json.load(f)["observed-directories"]["dirs"]
          for dir in data:
               observer = Observer()
               print(f"Observing {dir}")
               observer.schedule(event_handler, path=dir, recursive=False)
               observer.start()
               observers.append(observer)

     try:
          while True:
               time.sleep(1)
     except KeyboardInterrupt:
          print("Terminating 'File Observer'")
          for observer in observers:
               observer.stop()
     
     for observer in observers:
          observer.join()
