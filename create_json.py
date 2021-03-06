from tabulate import tabulate
import tmdbsimple as tmdb
import requests
import time
import json
import copy
import options
import os
import re

tmdb.API_KEY = options.TMDB_API_KEY


def search_tmdb(query, _type):
    search = tmdb.Search()
    if _type == 'MOVIE':
        response = search.movie(query=query)['results']
    else:
        response = search.tv(query=query)['results']

    if len(response) < 1:
        if _type == 'MOVIE':
            response = search.movie(query=query.split(' ')[0])['results']
        else:
            response = search.tv(query=query.split(' ')[0])['results']
    ids = []
    for title in response:
        if _type == 'MOVIE':
            ids.append([str(title['id']), title['title']])
        else:
            ids.append([str(title['id']), title['name']])
    result_dict = {}
    table_list = []
    count = 0
    for i in ids:
        if _type == 'MOVIE':
            f = tmdb.Movies(int(i[0])).info()
            languages = ['ja', 'cn', 'ko']
            if f['original_language'] not in languages:
                continue
        if _type != 'MOVIE':
            f = tmdb.TV(int(i[0])).info()
            if 'ja' not in f['languages'] and 'cn' not in f['languages']:
                continue

        result_dict[i[0] + '_' + _type] = {}
        result_dict[i[0] + '_' + _type]['title'] = i[1]
        if _type == 'MOVIE':
            g = 1
        else:
            g = f['number_of_seasons']
        entry = [count, i[1], g, i[0]]
        table_list.append(entry)
        count += 1

        if _type != 'MOVIE':
            for k in range(g + 1):
                try:
                    h = tmdb.TV_Seasons(int(i[0]), season_number=k).info()
                except Exception:
                    continue
                result_dict[i[0] + '_' + _type][str(k)] = {}
                for u in h['episodes']:
                    result_dict[i[0] + '_' + _type][str(k)][str(u['episode_number'])] = {
                        try:
                            name = u['name']
                        except KeyError:
                            name = None
                        'title': name,
                        'thumbnail': f"https://image.tmdb.org/t/p/original{u['still_path']}"
                        if u['still_path'] != None else None
                    }
        else:
            result_dict[i[0] + '_' + _type]['1'] = {}
            result_dict[i[0] + '_' + _type]['1']['1'] = {'title': i[1], 'thumbnail': f"https://image.tmdb.org/t/p/original{f['poster_path']}"}

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
                            format
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

    results = requests.post(
        url, json={'query': query, 'variables': variables}).json()

    result_list = results['data']['Page']['media']
    final_result = []
    result = []
    count = 0

    for anime in result_list:
        jp_title = anime['title']['romaji']
        ani_id = anime['id']
        _type = anime['format']

        entry = [count, jp_title, _type, ani_id]
        final_result.append(entry)
        count += 1

    headers = ['SlNo', "Title", 'format', "id"]
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
        # try:
        #     title = filename.split(' ')
        #     misc = title.pop(-1).split('.')[0]
        #     season_num = misc.split('E')[0].replace('S', '')
        #     episode_num = misc.split('E')[1]
        #     title = ' '.join(title).split('\\')[-1].split('/')[-1].strip()
        #     ep = {
        #         'ep': episode_num,
        #         'file': os.path.abspath(os.path.join(directory.replace('\\', '/'), filename)).replace('\\', '/'),
        #         'directory': os.path.abspath(directory).replace('\\', '/'),
        #         'timestamp': os.path.getctime(os.path.abspath(os.path.join(directory.replace('\\', '/'), filename)))
        #     }
        #     return title, season_num, ep
        # except IndexError:
        #     return
        try:
            groups = re.search("(.*)?\s+S(\d+)E(\d+)\.*",
                               filename.replace('\\', '/')).groups()
        except Exception:
            return

        title = groups[0].split('/')[-1]
        season_num = groups[1]
        ep = {
                'ep': groups[2],
                'file': os.path.abspath(os.path.join(directory.replace('\\', '/'), filename)).replace('\\', '/'),
                'directory': os.path.abspath(directory).replace('\\', '/'),
                'timestamp': os.path.getctime(os.path.abspath(os.path.join(directory.replace('\\', '/'), filename)))
            }
        return title, season_num, ep


default_config = options.jsonConfig


def write_to_config(data, config):
    with open(config, 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)


id_to_anime = {}


def read_config(config):
    if not os.path.isfile(default_config):
        write_to_config({"Known-Anime": {}}, default_config)
    with open(config, 'r') as f:
        return json.load(f)


cache_tmdb_requests = {}


def search_tmdb_id(tmdb_id, _type):
    if '{}_{}'.format(tmdb_id, _type) not in cache_tmdb_requests:
        if _type == 'MOVIE':
            f = tmdb.Movies(int(tmdb_id)).info()
            result_dict = {}
            result_dict['title'] = f['title']
            g = 1
            result_dict['1'] = {}
            result_dict['1']['1'] = {'title': f['title'], 'thumbnail': f"https://image.tmdb.org/t/p/original{f['poster_path']}"}
        else:
            f = tmdb.TV(int(tmdb_id)).info()
            result_dict = {}
            result_dict['title'] = f['name']
            g = f['number_of_seasons']
            for k in range(int(g + 1)):
                try:
                    h = tmdb.TV_Seasons(int(tmdb_id), season_number=k).info()
                except Exception:
                    continue
                result_dict[str(k)] = {}
                for u in h['episodes']:
                    result_dict[str(k)][str(u['episode_number'])] = {
                        try:
                            name = u['name']
                        except KeyError:
                            name = None
                        'title': name,
                        'thumbnail': f"http://image.tmdb.org/t/p/w1280_and_h720_bestv2{u['still_path']}"
                        if u['still_path'] != None else None
                    }
        cache_tmdb_requests['{}_{}'.format(
            tmdb_id, _type)] = copy.deepcopy(result_dict)
    else:
        result_dict = cache_tmdb_requests['{}_{}'.format(tmdb_id, _type)]
    return result_dict


def search_anilist_id(item_id):
    """
    The function to retrieve an anime's details.
    :param int item_id: the anime's ID
    :return: dict or None
    :rtype: dict or NoneType
    """
    query_string = """\
        query ($id: Int) {
            Media(id: $id, type: ANIME) {
                title {
                    romaji
                    english
                }
                format
            }
        }
    """
    _vars = {"id": item_id}
    url = 'https://graphql.anilist.co'
    r = requests.post(url, json={'query': query_string, 'variables': _vars})
    jsd = r.text
    try:
        jsd = json.loads(jsd)
    except ValueError:
        return None
    else:
        return jsd


pretty_print = {}
updated_config = {}


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
        if title not in pretty_print:
            print('Parsing: {}'.format(title.strip()))
            pretty_print[title] = ''
        ep['season_num'] = season
        id_to_anime = read_config(default_config)
        try:

            anilist_id = id_to_anime["Known-Anime"][title + '.' + season]['ani_id']
            _type = id_to_anime["Known-Anime"][title + '.' + season]['format']
            tmdb_dict = id_to_anime["Known-Anime"][title + '.' + season]['tmdb_dict']
            tmdb_id = id_to_anime["Known-Anime"][title + '.' + season]['tmdb_id']
            pretty_title = id_to_anime["Known-Anime"][title + '.' + season]['pretty_title']
            if 'last_modified' not in id_to_anime["Known-Anime"][title + '.' + season]:
                id_to_anime["Known-Anime"][title + '.' + season]['last_modified'] = time.time()
                write_to_config(id_to_anime, default_config)
            last_modified = id_to_anime["Known-Anime"][title + '.' + season]['last_modified']

            if last_modified - time.time() <= -options.TMDB_METADATA_UPDATE_INTERVAL:
                fg = str(anilist_id) + str(season) + str(tmdb_id)
                if fg not in updated_config:
                    updated_config[fg] = time.time()
                    print('Fetching new metadata for {} from theMovieDB.'.format(
                        pretty_title))
                    f = search_tmdb_id(tmdb_id.split('_')[0], _type)
                    if str(int(season)) in f:
                        tmdb_dict = {str(int(season)): f[str(int(season))]}
                    else:
                        tmdb_dict = f
                    id_to_anime["Known-Anime"][title + '.' + season]['tmdb_dict'] = tmdb_dict
                    id_to_anime["Known-Anime"][title + '.' + season]['last_modified'] = time.time()
                write_to_config(id_to_anime, default_config)

        except KeyError:
            table1, anilist_data = search_anilist(title)
            print(f'Anilist results for: {title} Season: {season}')
            print(table1)
            num = input("Select number: [0]: ")

            try:
                if 'e' in num:
                    value_bool = True
                else:
                    value_bool = False
                num = int(num.replace('e', '') if value_bool else num)
            except ValueError:
                num = 0

            ################################
            if num <= 50 and not value_bool:
                choice = anilist_data[num]
                anilist_id = str(choice[-1])
                _type = str(choice[-2])
            else:
                anilist_id = num
                anilist_dat = search_anilist_id(anilist_id)
                _type = anilist_dat['data']['Media']['format']

            table2, tmdb_dict = search_tmdb(title, _type)
            print('\n')
            ids = [x for x, i in tmdb_dict.items()]
            print(f'theMovieDB results for: {title}.')
            print(table2)
            num1 = input("Select number: [0]: ")
            print('\n----------------------------------------\n')
            try:
                if 'm' in num1:
                    _type = 'MOVIE'
                    num1 = int(num1.replace('m', ''))
                elif 't' in num1:
                    _type = 'TV'
                    num1 = int(num1.replace('t', ''))
                else:
                    num1 = int(num1)
            except ValueError:
                num1 = 0

            if num1 > 20:
                tmdb_dict = search_tmdb_id(num1, _type)
                tmdb_id = f'{num1}_{_type}'
            else:
                tmdb_dict = tmdb_dict[ids[num1]]
                tmdb_id = ids[num1]

            pretty_title = tmdb_dict['title']

            id_to_anime["Known-Anime"][title + '.' + season] = {}
            id_to_anime["Known-Anime"][title + '.' + season]['last_modified'] = time.time()
            id_to_anime["Known-Anime"][title + '.' + season]['ani_id'] = anilist_id
            id_to_anime["Known-Anime"][title + '.' + season]['tmdb_id'] = tmdb_id
            id_to_anime["Known-Anime"][title + '.' + season]['format'] = _type
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
                if int(ep['ep']) in [int(x) for x, y in tmdb_dict[key].items()]:
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
        fg = sorted(fg, key=lambda entry: int(
            entry['Episodes'][0]['season_num']))

        biggest_season = int(fg[-1]['Episodes'][0]['season_num'])
        # for season in fg:

        gg[ani_id]['Seasons'] = fg

        for kk in gg[ani_id]['Seasons']:
            if kk != {}:
                kk['Episodes'] = sorted(
                    kk['Episodes'], key=lambda entry: int(entry['ep']))


def save_to_json(data, path=options.jsonPath):
    """
    This function just saves the provided dict to a json file
    """
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

hh = {}
if options.FULL_SCAN:
    files_list = []
    for directory, __, files in os.walk(".", topdown=True):
        """
        This for loop makes a list
        with all the .mp4 files from the Current Working Directory
        and all the subdirectories
        """
        for file in files:
            if file.endswith(options.fileFormat):
                files_list.append([file, directory])
else:
    for directory, __, files in os.walk(".", topdown=True):
        """
        This for loop makes a list
        with all the .mp4 files from the Current Working Directory
        and all the subdirectories
        """
        for file in files:
            if file.endswith(options.fileFormat):
                add_json([[file, directory]], hh)

conv_list(hh)
save_to_json(hh)
