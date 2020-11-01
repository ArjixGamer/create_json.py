TMDB_API_KEY = 'XXXXXXXXXXXXXXXXXXX'
"""
This is the variable where you save the API V3 key for tmdb.
It will be used for downloading thumbnails and getting episode titles.
"""
TMDB_METADATA_UPDATE_INTERVAL = 259200 # three days in seconds, this will check if the last modified date was more than the seconds specified here
"""
When you generate a json, it saves in the config the last modified time.
You set an interval for how much is the minimal wait time until it tries to fetch new metadata from tmdb.
Don't set this value lower than a day, fetching new metadata longers the runtime, and if you manage a huge library time is precious.
"""
jsonPath = './database.json'
"""
This here is the filename that will be used to save the json.
If a folder doesn't exist there is no try/except block, so make sure the filepath you enter here is valid.
Else the code will error.
"""
jsonConfig = './config.json'
"""
Here the code saves data that can be reused at a later date.
It's to avoid making requests to tmdb as it makes the script slower.
"""
fileFormat = '.mp4'
"""
The file extension to look for, the code iterates over all the files in a directory.
If a file has the above extension it will be added to the list of items that should be processed.
"""
FULL_SCAN = False
"""
When set to True, the script will first scan all the files under the directory,
and then start parsing them, if set to False it will parse them as it scans the directory.
"""
