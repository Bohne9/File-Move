import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import json
import PyPDF2
import re


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
               print(f"Loaded rules...{data}")
               for suf in data:
                    # print(suf)
                    if path_suffix == suf:
                         rule = self.contains(path, path_suffix, data[suf])
                         if rule:
                              dest = rule['destination']
                              print(f'Matched! Move file {path} to {dest}')
                              shutil.move(path, dest)
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
               elif suffix in ["txt", "c", "java", "swift", "py", "json", "csv"]:
                    # Search in the file
                    return self.txtSearch(path, match)

     def pdfSearch(self, path, match):
          # open the pdf file
          object = PyPDF2.PdfFileReader(path)

          # get number of pages
          NumPages = object.getNumPages()

          # extract text and do the search
          for i in range(0, NumPages):
               PageObj = object.getPage(i)
               # print("this is page " + str(i)) 
               Text = PageObj.extractText() 
               # For each rule for pdf files
               for rule in match["rules"]:
                    # See if any rules match
                    for key in rule["contains-keyword"]:
                         print(f'Search for {key}')
                         ResSearch = re.search(key, Text)
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

     def on_created(self, event):
          print(f'event type: {event.event_type}  path : {event.src_path}')
          self.match(str(event.src_path))

     def on_moved(self, event):
          print(f'event type: {event.event_type}  path : {event.src_path}')
          self.match(str(event.src_path))




   

# Main
if __name__ == "__main__":
     # Create file Observer
     print("Running 'File Observer'")
     event_handler = MyHandler()
     observer = Observer()
     observer.schedule(event_handler, path='./test/', recursive=False)
     observer.start()

     try:
          while True:
               time.sleep(1)
     except KeyboardInterrupt:
          print("Terminating 'File Observer'")
          observer.stop()
     observer.join()