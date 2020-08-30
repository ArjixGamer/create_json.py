import requests
import json
import os
from tabulate import tabulate


def search_anilist(search, max_results=50):
    """
    This function builds a graphql request 
    for the anilist graphql api, it then uses all the results retrieved 
    to make a pretty table using the tabulate module 
    and it returns that table along with the raw results.
    """
    query = """
    query ($id: Int, $page: Int, $search: String, $type: MediaType) {
            Page (page: $page, perPage: 50) {
                    media (id: $id, search: $search, type: $type) {
                            id
                            title {
                                    english
                                    romaji
                            }
                            streamingEpisodes {
                                    title
                                    thumbnail
                            }
                    }
            }
    }
    """
    variables = {
            'search': search,
            'page': 1,
            'perPage': max_results,
            'type': 'ANIME'
    }
    url = 'https://graphql.anilist.co'

    results = requests.post(url, json={'query': query, 'variables': variables}).json()
    
    result_list = results['data']['Page']['media']
    final_result = []
    count = 0
    thumbnails = []
    for anime in result_list:
        jp_title = anime['title']['romaji']
        ani_id = anime['id']
        thumbnail = anime['streamingEpisodes']
        if bool(len(thumbnail)):
            thumbnail = [x['thumbnail'] for x in thumbnail]
            thumbnails.append(thumbnail)
        else:
            thumbnails.append(None)

        entry = [count, jp_title, ani_id]
        final_result.append(entry)
        count += 1

    headers = ['SlNo', "Title", "id"]
    table = tabulate(final_result, headers, tablefmt='psql')
    table = '\n'.join(table.split('\n')[::-1])
    return table, final_result

def extract_info(filename, directory):
    """
    This function parses the filename string to extract all the info
    the database may need. It returns a tuple with:
        the title,
        the season number
        and a dictionary with episode info.
    """
    #"One-Punch Man S01E01.mp4" => ("One Punch Man", 01, 04)
    groups = re.search("(.*)?\s+S(\d+)E(\d+)\.*", a).groups()

    #TODO: Catch whatever error this could return
    #TODO: Regex file path (I'm unaware of what input would look like)
    return groups[0], groups[1], {'ep': groups[2], 'file': os.path.abspath(os.path.join(directory.replace('\\', '/'), filename)).replace('\\', '/').replace('/var/www/html/', 'https://private.fastani.net/')}


default_config = './config.json'

def write_to_config(data, config):
    with open(config, 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)

id_to_anime = {}
def read_config(config):
    if not os.path.isfile(config):
        write_to_config({"Known-Anime": {}}, default_config)
    with open(config, 'r') as f:
        return json.load(f)


def add_json(files, gg):
    """
    This function creates a dict with the layout that is desired
    All the try excepts are to make that dict, 
    because it will error if a key is missing 
    thats why i have try except blocks to make the necessary and only needed keys
    """
    for a in files:
        f = extract_info(a[0], a[1])
        if type(f) == type(None):
            continue
        title, season, ep = f
        try:
            id_to_anime = read_config(default_config)
            ff = id_to_anime["Known-Anime"][title + '.' + season]
        except KeyError:
            table, ff = search_anilist(title)
            print(f'Search results for {title} season {season}')
            print(table)
            num = input("Select number: [0]: ")
            try:
                num = int(num)
            except ValueError:
                num = 0
            if num <= 50:
                choice = ff[num] if num != '' else ff[0]
                ff = str(choice[-1])
            else:
                ff = num
            id_to_anime["Known-Anime"][title + '.' + season] = ff
            write_to_config(id_to_anime, default_config)
        try:
            try:
                gg[ff]['Seasons'][season]['Episodes'].append(ep)
            except:
                gg[ff]['Seasons'][season] = {}
                gg[ff]['Seasons'][season]['Episodes'] = []
        except:
            try:
                gg[ff]['Seasons'] = {}
                gg[ff]['Seasons'][season] = {}
                gg[ff]['Seasons'][season]['Episodes'] = []
                gg[ff]['Seasons'][season]['Episodes'].append(ep)
            except KeyError:
                gg[ff] = {}
                gg[ff]['Seasons'] = {}
                gg[ff]['Seasons'][season] = {}
                gg[ff]['Seasons'][season]['Episodes'] = []
                gg[ff]['Seasons'][season]['Episodes'].append(ep)

def conv_list(gg):
    """
    This function is responsible for 
    1. taking the Seasons dict inside the generated dict from the above function
    2. Converting it to an array
    3. Sort the array to the correct seasons/episodes order
    """
    for a, b in gg.items():
        seasons = gg[a]['Seasons']
        fg = []
        for c, d in seasons.items():
            fg.append(d)
        fg = sorted(fg, key=lambda entry: int(entry['Episodes'][0]['file'].split(' ').pop(-1).split('.')[0].split('E')[0].replace('S', '')))
        gg[a]['Seasons'] = fg

        for kk in gg[a]['Seasons']:
            kk['Episodes'] = sorted(kk['Episodes'], key=lambda entry: int(entry['file'].split(' ').pop(-1).split('.')[0].split('E')[1]))


def save_to_json(data, path='./database.json'):
    """
    This function just saves the provided dict to a json file
    """
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


files_list = []

for directory, __, files in os.walk("."):
    """
    This for loop makes a list 
    with all the .mp4 files from the Current Working Directory
    and all the subdirectories
    """
    for file in files:
        if file.endswith('.mp4'):
            files_list.append([file, directory])
hh = {}
add_json(files_list, hh)
conv_list(hh)
save_to_json(hh)
