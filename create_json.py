import requests
import json
import os
from tabulate import tabulate
import tmdbsimple as tmdb


tmdb.API_KEY = 'TMDB_API_v3_KEY'


def search_tmdb(query):
    search = tmdb.Search()
    response = search.tv(query=query)['results']
    if len(response) < 1:
        response = search.tv(query=query.split(' ')[0])['results']
    ids = []
    for title in response:
        ids.append([str(title['id']), title['name']])
    result_dict = {}
    table_list = []
    count = 0
    for i in ids:
        f = tmdb.TV(int(i[0])).info()
        if not 'ja' in f['languages'] and not 'cn' in f['languages']:
            continue
        result_dict[i[0]] = {}
        result_dict[i[0]]['title'] = i[1]
        g = f['number_of_seasons']
        entry = [count, i[1], g, i[0]]
        table_list.append(entry)
        count += 1
        for k in range(g + 1):
            if k == 0:
                continue
            h = tmdb.TV_Seasons(int(i[0]), season_number=k).info()
            result_dict[i[0]][str(k)] = {}
            for u in h['episodes']:
                result_dict[i[0]][str(k)][str(u['episode_number'])] = {
                'title': u['name'], 
                'thumbnail': f"https://image.tmdb.org/t/p/original/{u['still_path']}" 
                if u['still_path'] != None else None
                }

    headers = ['SlNo', "Title", "Total Seasons", 'id']
    table = tabulate(table_list, headers, tablefmt='psql')
    table = '\n'.join(table.split('\n')[::-1])
    return table, result_dict

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
    result = []
    count = 0

    for anime in result_list:
        jp_title = anime['title']['romaji']
        ani_id = anime['id']

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
    #TODO: use regex for the season and episode number extraction
    # re.search("S\d+E\d+", "One-Punch Man S01E01.mp4").group() ==> 'S01E01'
    try:
        title = filename.split(' ')
        misc = title.pop(-1).split('.')[0]
        season_num = misc.split('E')[0].replace('S', '')
        episode_num = misc.split('E')[1]
        title = ' '.join(title).split('\\')[-1].split('/')[-1].strip()
        ep = {
            'ep': episode_num, 
            'file': os.path.abspath(os.path.join(directory.replace('\\', '/'), filename)).replace('\\', '/'), 
            'directory': os.path.abspath(directory).replace('\\', '/'), 
            'timestamp': os.path.getctime(os.path.abspath(os.path.join(directory.replace('\\', '/'), filename)))
            }
        return title, season_num, ep
    except IndexError:
        return


default_config = './config.json'


def write_to_config(data, config):
    with open(config, 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)


id_to_anime = {}


def read_config(config):
    if not os.path.isfile(default_config):
        write_to_config({"Known-Anime": {}}, default_config)
    with open(config, 'r') as f:
        return json.load(f)


def search_tmdb_id(tmdb_id):
    f = tmdb.TV(int(tmdb_id)).info()
    result_dict = {}
    result_dict['title'] = f['name']
    g = f['number_of_seasons']
    for k in range(g + 1):
        if k == 0:
            continue
        h = tmdb.TV_Seasons(int(tmdb_id), season_number=k).info()
        result_dict[str(k)] = {}
        for u in h['episodes']:
            result_dict[str(k)][str(u['episode_number'])] = {
                'title': u['name'], 
                'thumbnail': f"http://image.tmdb.org/t/p/w1280_and_h720_bestv2{u['still_path']}" 
                if u['still_path'] != None else None
            }
    return result_dict


def add_json(files, gg):
    """
    This function creates the dictionary that will be then converted and exported as a json.
    It also manages the config.json with all the data needed to avoid promting the user for the anime result.
    """
    thumbnails_dict = {}
    for a in files:
        f = extract_info(a[0], a[1])
        if type(f) == type(None):
            continue
        title, season, ep = f
        ep['season_num'] = season
        id_to_anime = read_config(default_config)
        try:
            anilist_id = id_to_anime["Known-Anime"][title + '.' + season]['ani_id']
            tmdb_dict = id_to_anime["Known-Anime"][title + '.' + season]['tmdb_dict']
            tmdb_id = id_to_anime["Known-Anime"][title + '.' + season]['tmdb_id']
            pretty_title = id_to_anime["Known-Anime"][title + '.' + season]['pretty_title']

        except KeyError: 
            table1, anilist_id = search_anilist(title)
            table2, tmdb_dict = search_tmdb(title)
            print(f'Anilist results for: {title} Season: {season}')
            print(table1)
            num = input("Select number: [0]: ")
            print('\n')
            ids = [x for x, i in tmdb_dict.items()]
            print(f'theMovieDB results for: {title}.')
            print(table2)
            num1 = input("Select number: [0]: ")
            print('\n----------------------------------------\n')

            try:
                num = int(num)
            except ValueError:
                num = 0
            try:
                num1 = int(num1)
            except ValueError:
                num1 = 0

            if num <= 50:
                choice = anilist_id[num]
                anilist_id = str(choice[-1])
            else:
                anilist_id = num

            if num1 > 20:
                tmdb_dict = search_tmdb_id(num1)
                tmdb_id = num1
            else:
                tmdb_dict = tmdb_dict[ids[num1]]
                tmdb_id = ids[num1]

            pretty_title = tmdb_dict['title']
            id_to_anime["Known-Anime"][title + '.' + season] = {}
            id_to_anime["Known-Anime"][title + '.' + season]['ani_id'] = anilist_id
            id_to_anime["Known-Anime"][title + '.' + season]['tmdb_id'] = tmdb_id
            if str(int(season)) in tmdb_dict:
                tmdb_dict = {str(int(season)): tmdb_dict[str(int(season))]}
            id_to_anime["Known-Anime"][title + '.' + season]['tmdb_dict'] = tmdb_dict
            id_to_anime['Known-Anime'][title + '.' + season]['pretty_title'] = pretty_title
            write_to_config(id_to_anime, default_config)

        if anilist_id not in gg:
            gg[anilist_id] = {}
        if 'Seasons' not in gg[anilist_id]:
            gg[anilist_id]['Seasons'] = {}
        if season not in gg[anilist_id]['Seasons']:
            gg[anilist_id]['Seasons'][season] = {}
        if 'Episodes' not in gg[anilist_id]['Seasons'][season]:
            gg[anilist_id]['Seasons'][season]['Episodes'] = []

        for key, value in tmdb_dict.items():
            if key == 'title':
                continue

            if int(season) == int(key):
                if str(int(ep['ep'])) in value:
                    dat = value[str(int(ep['ep']))]
                    thumb_dir = os.path.join(ep['directory'], 'thumbs')
                    if bool(dat['thumbnail']):

                        if not os.path.isdir(thumb_dir):
                            os.mkdir(thumb_dir)
                        thumb = os.path.join(thumb_dir, f'''{anilist_id}_thumbnail_{ep['ep']}.jpg''')

                        if not os.path.isfile(thumb):
                            with open(thumb, 'wb') as f:
                                print(f'Downloading: {thumb}')
                                f.write(requests.get(dat['thumbnail']).content)
                    else:
                        thumb = 'N/A'

                    ep['thumb'] = thumb
                    ep['title'] = dat['title']

        gg[anilist_id]['Seasons'][season]['Episodes'].append(ep)
        gg[anilist_id]['Seasons'][season]['pretty_title'] = pretty_title


def conv_list(gg):
    """
    This function is responsible for 
    1. taking the Seasons dict inside the generated dict from the above function
    2. Converting it to an array
    3. Sort the array to the correct seasons order
    """
    for ani_id, b in gg.items():
        seasons = gg[ani_id]['Seasons']
        fg = []
        for c, d in seasons.items():
            fg.append(d)
        fg = sorted(fg, key=lambda entry: int(entry['Episodes'][0]['file'].split(' ').pop(-1).split('.')[0].split('E')[0].replace('S', '')))

        gg[ani_id]['Seasons'] = fg

        for kk in gg[ani_id]['Seasons']:
            kk['Episodes'] = sorted(kk['Episodes'], key=lambda entry: int(entry['ep']))


def save_to_json(data, path='./database.json'):
    """
    This function just saves the provided dict to a json file
    """
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


files_list = []
# os.chdir('./html')
for directory, __, files in os.walk(".", topdown=True):
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
