#!/usr/local/bin/python3

import praw
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
import time
import threading
import random
import json
from os import listdir
from os.path import isfile, join


# Initialize reddit object with .ini file.
reddit = praw.Reddit('Authentication')

# Imgur authentication information.
client_id = 'insert_client_id'
client_secret = 'insert_client_secret'

# Connect to imgur.
try:
    client = ImgurClient(client_id, client_secret)

except ImgurClientError as e:
    print(e.error_message)
    print(e.status_code)

# Cache image files so that we don't repost the same image.
# This cache is cleared every x days. x is provided in the input.json file.
cache = []

# Continuously pick a random image from the imgur album and post it to the input
# subreddit. Wait for a given number of hours before posting again.
# Cache images so the are not repeated. Clear cache according to input
# frequency.
def main():
    # Check if authentication information is correct.
    try:
        print("Successfully logged into Reddit with username ", reddit.user.me(),
                ".", sep = '')

    except Exception as e:
        print(e)
        return

    # Load JSON file for album id, frequency of posts, subreddit, and
    # frequency to repeat image posts.
    with open('input.json') as input_file:
        input = json.load(input_file)

    # Execute thread to clear cache.
    thread = threading.Thread(target = clear_cache, args =
            (input['repeat_frequency'],))
    thread.start()

    while(True):
        # Get all images in the imgur album.
        try:
            images = client.get_album_images(input['album_id'])
            for image in images:
                print(image.link)

        except Exception as e:
            print(e)
            break;

        # Pick a random image until we get one that isn't cached.
        while(True):
            index = random.randrange(0, len(images))

            # Cache miss. Post this image.
            link = images[index].link
            if link not in cache:
                print("Caching image ", link, ".", sep = '')
                cache.append(link)
                post(link, input['subreddit'])
                break;

        # Wait for a specific number of hours. This is provided in the
        # input.json file.
        hours = input['frequency']
        print("sleeping for", hours, "hours...")

        # Convert hours to seconds.
        time.sleep(hours * 60 * 60)


def post(link, subreddit):
    print("Posting the image ", link, " to the subreddit ", subreddit,
            "...", sep = '')

    sub = reddit.subreddit(subreddit)
    sub.submit("Image of the day! (Test)", url = link)


def clear_cache(days):
    print("Sleeping for", days, "days before clearing the cache...")

    # Convert days to seconds.
    time.sleep(days * 24 * 60 * 60)

    print("Cache cleared.")
    del cache[:]


if __name__ == '__main__':
    main()
