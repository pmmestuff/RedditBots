#!/usr/local/bin/python3

import praw
import time
import json
from os import listdir
from os.path import isfile, join


# Initialize reddit object with .ini file. Continuously pick a random image from
# the album directory and post it to the input subreddit. Wait for a given
# number of hours before posting again.
reddit = praw.Reddit('Authentication')

def main():
    print("Successfully logged into Reddit with username ", reddit.user.me(),
            ".", sep = '')

    # Load JSON file for album directory, frequency of posts, and subreddit.
    with open('input.json') as input_file:
        input = json.load(input_file)

    while(True):
        files = [f for f in listdir(input['album_path'])
                if isfile(join(input['album_path'], f))]

        for f in files:
            print(f)





if __name__ == '__main__':
    main()
