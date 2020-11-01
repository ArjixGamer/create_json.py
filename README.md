## Create JSON

A python script to generate a database.json file, it walks thought all the files from the [CWD](https://en.wikipedia.org/wiki/Working_directory) and all its [Subdirectories](https://www.computerhope.com/jargon/s/subdirec.htm) and collects info from all the [.mp4](https://en.wikipedia.org/wiki/MPEG-4_Part_14) files.

## Disclaimer
This project uses both the AniList and theMovieDB API's, thanks to tmdb I can take all the usefull episode metadata!

<img src="https://i.imgur.com/Ak72T73.png" alt="AniList" width=250 height=250> <img src="https://www.themoviedb.org/assets/2/v4/logos/v2/blue_square_1-5bdc75aaebeb75dc7ae79426ddd9be3b2be1e342510f8202baf6bffa71d7f5c4.svg" alt="tmdb" width=250 height=250>

## Requirements

1. [Python](https://www.python.org/) 3.7 and above with pip.
2. All files must follow [this](#Naming-Scheme) naming scheme
3. The Python Modules [Tabulate](https://pypi.org/project/tabulate/), [Requests](https://pypi.org/project/requests/) & [tmdb_simple](https://pypi.org/project/tmdbsimple/).
4. An API v3 key for [theMovieDB](https://www.themoviedb.org/settings/api).



## USAGE

1. Place the script in the root folder of all your anime.

2. Edit the options.py with the required settings. (for now only the api key and metadata update interval)

3. Open a command window at that same directory

4. Type ``python create_json.py`` and hit the [RETURN](https://pc.net/helpcenter/answers/keyboard_return_key#:~:text=The%20Return%20key%20has%20the,paper%20to%20the%20next%20line) key.

5. The script will make searches to [AniList](https://anilist.co) and print a pretty table. The user will be prompted to select a number.

6. When all the unknown anime are searched and found the script will save a database.json with [this](#JSON-Structure) structure, it will also save another JSON file with all the known anime, so that on the 2nd run and onwards it won't search again for the same anime, only for the unknown ones.

## Variables you can change

All variables you can change are located in the config.py file. Most of them are self explanatory but here is what they do.

| Variables    | Description                                                                                                                                                |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| TMDB_API_KEY | You store the API key you got from tmdb.                                                                                                                   |
| jsonConfig   | Where your saved configs are, by default it's '\./config\.json'                                                                                            |
| jsonPath     | The full filepath where the database will be stored at.\nNote: the script does not read what the database.json contains, it just saves.                    |
| fileFormat   | The file format which info is collected from, by default it's '\.mp4'                                                                                      |
| FULL_SCAN    | If set to True it will scan all the files in a directory first before parsing them, if set to False it will scan on the go.                                |
| TMDB_METADATA_UPDATE_INTERVAL | The seconds it will wait until it updates the saved metadata from the config.json.                                                        |

## Naming Scheme

```
/Anime
	/Season {Number}
		Anime S{Number}E{Number}.mp4
```

Where ``{Number}`` is a full number, in other words an Integer.

```
S{Number} ==> S01 (Season 1)

E{Number} ==> E01 (Episode 1)
```

For Example:

```
/One-Punch Man
	/Season 1
		One-Punch Man S01E01.mp4
		One-Punch Man S01E02.mp4
```


Note:

If the anime is a movie then simply name it as Season 1 Episode 1


e.g "Totoro S01E01.mp4"


## JSON Structure

The database.json will look like this:

```json
{
    "12431": {
        "Seasons": [
            {
                "Episodes": [
                    {
                        "ep": "001",
                        "file": "H:/Anime/Space Brothers/Season 1/Space Brothers S01E001.mp4",
                        "directory": "H:/Anime/Space Brothers/Season 1",
                        "timestamp": 1600200007.283316,
                        "season_num": "01",
                        "thumb": "H:/Anime/Space Brothers/Season 1/thumbs/12431_thumbnail_001.jpg",
                        "title": "Little Brother Hibito and Big Brother Mutta"
                    },
                    {
                        "ep": "002",
                        "file": "H:/Anime/Space Brothers/Season 1/Space Brothers S01E002.mp4",
                        "directory": "H:/Anime/Space Brothers/Season 1",
                        "timestamp": 1600204968.1122825,
                        "season_num": "01",
                        "thumb": "H:/Anime/Space Brothers/Season 1/thumbs/12431_thumbnail_002.jpg",
                        "title": "My Shining Star"
                    },
                    {
                        "ep": "003",
                        "file": "H:/Anime/Space Brothers/Season 1/Space Brothers S01E003.mp4",
                        "directory": "H:/Anime/Space Brothers/Season 1",
                        "timestamp": 1600208432.2625673,
                        "season_num": "01",
                        "thumb": "H:/Anime/Space Brothers/Season 1/thumbs/12431_thumbnail_003.jpg",
                        "title": "The Man with the Advantage and the Running Female Doctor"
                    },
                    {
                        "ep": "004",
                        "file": "H:/Anime/Space Brothers/Season 1/Space Brothers S01E004.mp4",
                        "directory": "H:/Anime/Space Brothers/Season 1",
                        "timestamp": 1600251484.1724074,
                        "season_num": "01",
                        "thumb": "H:/Anime/Space Brothers/Season 1/thumbs/12431_thumbnail_004.jpg",
                        "title": "Next to Hibito"
                    },
                    {
                        "ep": "005",
                        "file": "H:/Anime/Space Brothers/Season 1/Space Brothers S01E005.mp4",
                        "directory": "H:/Anime/Space Brothers/Season 1",
                        "timestamp": 1600287264.3941905,
                        "season_num": "01",
                        "thumb": "H:/Anime/Space Brothers/Season 1/thumbs/12431_thumbnail_005.jpg",
                        "title": "Days of Missing"
                    }
                ],
                "pretty_title": "Space Brothers"
            }
        ]
    }
}
```

It has the anilist id as the key entry, and inside it a json that has an array of seasons with their files.
