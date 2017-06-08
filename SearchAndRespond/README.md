# SearchAndRespond

Reddit bot to find certain keywords or phrases in reddit comments on given
subreddits. Once keywords are found a response can be sent to the user via
reddit comment or private message.

Input is taken in JSON format in the 'responses.json' file.

The script uses an SQLite database to cache comments that it has replied to.
