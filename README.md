# Automatic file moving script

## Abilities

- Listen for new files in specific directories
- Move files which names match a given regex
- Search in pdf files for text and move file if some text in the pdf matches a given regex

## Requirements

- python
- 

## Install & Setup

- Download code
- Put the code into a directory of your choice
- create a file called **file-move.json**

```
{
   "observed-directories": {
        "dirs": [
             "/My/path/to/observe",
             "/My/second/path/to/observe",
             "..."
        ]
   },
   "pdf": {
    "rules": [
      {
        "active": true,
        "description": "The description of my rule"
        "contains-keyword": [
          "regex for the text/ keywords to search for in the pdf file"
        ],
        "destination": "/My/destination/path/where/the/files/that/match/should/be/moved/to"
      }
    ]
   },
   "(jpg|jpeg|png)": {
    "rules": [
      {
        "active": true,
        "description": "The description of my rule"
        "name-contains": [
          "regex to match the file name"
        ],
        "destination": "/My/destination/path/where/the/files/that/match/should/be/moved/to"
      }
    ]
   },
   "some other regex to match the suffix of the added file": {
    "rules": [
      {
        "active": false,
        "description": "The description of my rule"
        "name-contains": [
          "regex to match the file name"
        ],
        "destination": "/My/destination/path/where/the/files/that/match/should/be/moved/to"
      }
    ]
   }

