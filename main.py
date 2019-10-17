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

#TODO:
# - Logging
# - Fix crash when file already exists in destination directory
# - Add more types
# - Add support for file name matches
home = fs.expanduser("~")
file_move_json = home + "/.file_move/file-move.json"
log_file = home + "/.file_move/logs/app.log"

class MyHandler(FileSystemEventHandler):

     def match(self, path):
          # Look for the suffix of the path
          suffix = path.split('.')

          # List is empty. Return bc something is wrong with the path
          if not suffix:
               # TODO: Logging
               print("no suffix")
               return
          path_suffix = suffix[-1]
          print(path_suffix)

          # Open the file move rules and look for matching rules
          with open('./file-move-rules.json', 'r') as rules:
               # Load JSON data
               data = json.load(rules)
               print(f'Loaded rules...{data}')
               for suf in data:
                    # print(suf)
                    # if path_suffix == suf:
                    if re.search(suf, path_suffix):
                         # See if anything matches
                         rule = self.contains(path, path_suffix, data[suf])
                         # If True -> found something
                         if rule:
                              dest = rule['destination']
                              # print(f'Matched! Move file {path} to {dest}')
                              # shutil.move(path, dest)
                              self.move_file(path, dest)
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
               elif re.search("(txt|c)", suffix):
                    # Search in the file
                    return self.txtSearch(path, match)
               else:
                    print("Something is wrong")


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

     def move_file(self, source, dest):
          shutil.move(source, dest)
          logging.info(f'Moved file {source} to {dest}')

     def on_created(self, event):
          print(f'event type: {event.event_type}  path : {event.src_path}')
          self.match(str(event.src_path))

     def on_moved(self, event):
          print(f'event type: {event.event_type}  path : {event.src_path}')
          self.match(str(event.src_path))

def start_routine():
     if not fs.isdir(home + "/.file_move"):
          os.mkdir(home + "/.file_move")
          
          os.mkdir(home + "/.file_move/logs")


# Main
if __name__ == "__main__":
     start_routine()
     # Config logging
     logging.basicConfig(filename=log_file, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
     # Create file Observer
     print("Running 'File Observer'")
     observers = []
     event_handler = MyHandler()
     # observer = Observer()
     # observer.schedule(event_handler, path='./test/', recursive=False)
     # observer.start()

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
