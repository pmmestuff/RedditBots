#!/usr/local/bin/python3

import praw
import time
from pprint import pprint
import json
import sqlite3
import threading


# Initialize reddit object with .ini file.
reddit = praw.Reddit('Authentication')

connection = sqlite3.connect('comment_cache.db')
cursor = connection.cursor()

# Setup reddit object and phrases to search for.
# Begin searching through given subreddit(s).
def main():
    print("Successfully logged into Reddit with username ", reddit.user.me(),
            ".", sep = '')

    # Execute thread to remove old/downvoted replies.
    thread = threading.Thread(target = cleanup)
    thread.start()

    # Create comment cache table if it doesn't already exist.
    cursor.execute(''' CREATE TABLE IF NOT EXISTS comment_cache (id text UNIQUE) ''')

    ''' Load JSON file for subreddit(s), phrases, responses, and other options.
        The 'subreddits' array contains the subreddit(s) to search over. Each of
        the subreddit objects stores the sorting to search over (hot, top, new)
        and the number of submissions to search over.
        The 'my_username' variable is the username you wish to send notifications
        to.
        The JSON file also contains an array of responses. Each response has a
        set of phrases that trigger the response itself. The response object
        also has flags for sending the response as a comment reply to the user,
        sending the user a private message, and messaging yourself.
    '''
    with open('responses.json') as responses_file:
        responses = json.load(responses_file)

    # Continuously search for phrases in comments of given subreddit(s).
    while(True):
        # Gather all phrases to search for.
        phrases = []
        for response in responses["responses"]:
            for phrase in response["phrases"]:
                phrases.append(phrase)

        print("Phrases:", phrases)

        # 'sub' is the JSON object, while 'subreddit' is the reddit object.
        for sub in responses["subreddits"]:
            # TODO: Error handling for bad subreddit names, sorting types, and
            # num_post values.
            subreddit = reddit.subreddit(sub["name"])

            print("Searching", sub["num_posts"], "posts on",
                    subreddit.display_name, "with", sub["sort"], "sorting...")

            search_and_respond(subreddit, sub["sort"], sub["num_posts"],
                    phrases)


# Search through all comments in a subreddit and look for all phrases.
def search_and_respond(subreddit, sorting, num_posts, phrases):
    # Determine the sorting of the subreddit and search through num_posts posts
    # in that sorting.
    sorted_sub = subreddit.hot(limit = num_posts)

    if sorting == "top":
        sorted_sub = subreddit.top(limit = num_posts)
    elif sorting == "new":
        sorted_sub = subreddit.new(limit = num_posts)

    for submission in sorted_sub:
        # Skip stickied submissions.
        if submission.stickied:
            continue

        # NOTE: Look into changing this. Not sure if I want to search through
        # the extended comment trees.
        submission.comments.replace_more(limit = 0)

        print("Searching comments in submission: ", submission.title, ".",
                sep = '')

        all_comments = submission.comments.list()

        # Look for each phrase in each comment's body and respond if we have not
        # already.
        for comment in all_comments:
            for phrase in phrases:
                if phrase in comment.body:
                    print("Found a comment including the phrase: ", phrase, ".",
                            sep = '')
                    respond(phrase, comment.id)


# Reply to a found comment. Confirm that we have not already responded to the
# comment.
def respond(phrase, comment_id):
    cursor.execute(''' SELECT id FROM comment_cache WHERE id=? ''', (comment_id,))
    data = cursor.fetchall()

    if len(data) == 0:
        print("Cache miss. Caching comment with id ", comment_id, ".", sep = '')
        cursor.execute(''' INSERT INTO comment_cache VALUES (?) ''', (comment_id,))
    else:
        print("Cache hit. Not replying to comment.")
        return

    print("Responding to a comment...")

    # Lookup response associated with the found phrase.
    with open('responses.json') as responses_file:
        responses = json.load(responses_file)

    for response in responses["responses"]:
        if phrase in response["phrases"]:
            # Reply to the comment.
            if response['comment']:
                comment = reddit.comment(comment_id)
                comment.reply(response['response'])

            # Send the user a private message with the provided reponse.
            if response['pm']:
                author = comment.author

                # Check whether to use a different response for private messages.
                if response['pm_response'] != "":
                    author.message(response['pm_subject'],
                            response['pm_response'])
                else:
                    author.message(response['pm_subject'], response['response'])

            # Send your own account a pm when the bot makes a reply.
            if response['pm_me']:
                me = reddit.get_redditor(responses['benagin'])
                comment = reddit.comment(commentid)
                me.message("Bot has made a reply.", "The bot has responded to" +
                        "the comment\n" + comment.body + "\n from the" +
                        "submission\n" + comment.submission.title + ".")


# Remove comment replies that have been downvoted below 1 in case the reply was
# not relative.
def cleanup():
    print("Cleaning up downvoted comments.")

    while(True):
        my_account = reddit.user.me()

        my_comments = my_account.comments.new(limit=None)

        # Delete all comments with < 1 point.
        for comment in my_comments:
            if comment.score < 1:
                print("Deleting comment ", comment.id, "...", sep = '')
                comment.delete()

        # Sleep for 30 minutes and continue checking.
        time.sleep(1800)


if __name__ == '__main__':
    main()
