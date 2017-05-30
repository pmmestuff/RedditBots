#!/usr/local/bin/python3

import praw

reddit = praw.Reddit('Authentication')
print(reddit.user.me())

