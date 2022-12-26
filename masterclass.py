import requests, json, sys, re, os
import cloudscraper
from slugify import slugify

class Masterclass(object):
    def __init__(
        self,
        cookie,
        download_path=os.environ.get('FILE_PATH', './Masterclass'),
        pk='BCpkADawqM3U3jTXbQuJ1_Zax4NTXCtyzMNzIfN8Bjg8dL-yOcLMYks2o8BFWTuFTsX-u783Ai83BGt-6y95dLi4XyKUeqrzHOsotl7boZ8qH7jlJhdIAfLNg97y5ONlbLhmEy_zgOt2-F-c',
        brightcove_account_id=5344802162001,
    ):
        self.cookie = cookie.strip().strip('"')
        self.download_path = download_path
        self.pk = pk.strip()
        self.brightcove_account_id = brightcove_account_id
        self.pythonversion = 3 if sys.version_info >= (3, 0) else 2

    def is_unicode_string(self, string):
        if (self.pythonversion == 3 and isinstance(string, str)) or (self.pythonversion == 2 and isinstance(string, str)):
            return True

        else:
            return False

    def download_class_by_url(self, url):
        m = re.match(r'https://www.masterclass.com/classes/.*?(.+)', url)

        if not m:
            raise Exception('Failed to parse class ID from URL')

        self.download_course_by_class_id(m.group(1))

    def download_course_by_class_id(self, class_id):
        data = self.fetch_course_data_by_class_id(class_id=class_id)

        teacher_name = None
        if 'instructor_name' in data:
            teacher_name = data['instructor_name']

        if not teacher_name and 'instructors' in data and len(data['instructors']) != 0 and 'name' in data['instructors'][0]:
            teacher_name = data['instructors'][0]['name']

        if not teacher_name:
            raise Exception('Failed to read teacher name from data')

        if self.is_unicode_string(teacher_name):
            teacher_name = teacher_name.encode('ascii', 'replace')

        title = None
        if 'slug' in data:
            title = data['slug']
        elif 'title' in data:
            title = data['title']
        else:
            raise Exception('Failed to read title from data')

        if self.is_unicode_string(title):
            title = title.encode('ascii', 'replace')  # ignore any weird char

        base_path = os.path.abspath(
            os.path.join(
                self.download_path,
                slugify(teacher_name),
                slugify(title),
            )
        ).rstrip('/')

        if not os.path.exists(base_path):
            os.makedirs(base_path)

        for s in data['chapters']:
            video_id = None
            if 'brightcove_video_id' in s:
                video_id = s['brightcove_video_id']

            if not video_id:
                raise Exception('Failed to read video ID from data')

            s_title = None
            if 'title' in s:
                s_title = s['title']
            elif 'slug' in s:
                s_title = s['slug']
            else:
                raise Exception('Failed to read video title from data')

            if self.is_unicode_string(s_title):
                s_title = s_title.encode('ascii', 'replace')

            file_name = '{} - {}'.format(
                str(s['number']).zfill(2),
                slugify(s_title),
            )

            self.download_video(
                fpath='{base_path}/{session}.mp4'.format(
                    base_path=base_path,
                    session=file_name,
                ),
                video_id=video_id,
            )

            print('')

    def fetch_course_data_by_class_id(self, class_id):
        url = 'https://www.masterclass.com/jsonapi/v1/courses/{}?deep=true'.format(class_id)
        scraper = cloudscraper.create_scraper(
            browser={
                
            },
            delay=10
        )

        res = scraper.get(
            url,
            headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'cookie': self.cookie,
            }
        )

        if not res.status_code == 200:
            raise Exception('Fetch error, code == {}'.format(res.status_code))

        return res.json()

    def download_video(self, fpath, video_id):
        meta_url = 'https://edge.api.brightcove.com/playback/v1/accounts/{account_id}/videos/{video_id}'.format(
            account_id=self.brightcove_account_id,
            video_id=video_id,
        )

        scraper = cloudscraper.create_scraper(
            browser={
                'custom': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            },
            delay=10
        )

        meta_res = scraper.get(
            meta_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                'Accept-Encoding': 'none',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Accept': 'application/json;pk={}'.format(self.pk),
                'Origin': 'https://www.masterclass.com'
            }
        )

        if meta_res.status_code != 200:
            return

        if meta_res.json()['sources'][2]['container'] == 'MP4' and 'src' in meta_res.json()['sources'][2]:
            dl_url = meta_res.json()['sources'][2]['src']
            # break
        else:
            dl_url = meta_res.json()['sources'][0]['src']

        print('Downloading {}...'.format(fpath))

        if os.path.exists(fpath):
            print('Video already downloaded, skipping...')
            return

        with open(fpath, 'wb') as f:
            response = requests.get(dl_url, allow_redirects=True, stream=True)
            total_length = response.headers.get('content-length')

            if not total_length:
                f.write(response.content)

            else:
                dl = 0
                total_length = int(total_length)

                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                    sys.stdout.flush()

            print('')

def splash():

    print(r""" 
                                                                                                               
          ____                                                                                                 
        ,'  , `.                       ___                             ,--,                                    
     ,-+-,.' _ |                     ,--.'|_                         ,--.'|                                    
  ,-+-. ;   , ||                     |  | :,'           __  ,-.      |  | :                                    
 ,--.'|'   |  ;|            .--.--.  :  : ' :         ,' ,'/ /|      :  : '               .--.--.   .--.--.    
|   |  ,', |  ': ,--.--.   /  /    .;__,'  /    ,---. '  | |' |,---. |  ' |    ,--.--.   /  /    ' /  /    '   
|   | /  | |  ||/       \ |  :  /`.|  |   |    /     \|  |   ,/     \'  | |   /       \ |  :  /`./|  :  /`./   
'   | :  | :  |.--.  .-. ||  :  ;_ :__,'| :   /    /  '  :  //    / '|  | :  .--.  .-. ||  :  ;_  |  :  ;_     
;   . |  ; |--' \__\/: . . \  \    `.'  : |__.    ' / |  | '.    ' / '  : |__ \__\/: . . \  \    `.\  \    `.  
|   : |  | ,    ," .--.; |  `----.   |  | '.''   ;   /;  : |'   ; :__|  | '.'|," .--.; |  `----.   \`----.   \ 
|   : '  |/    /  /  ,.  | /  /`--'  ;  :    '   |  / |  , ;'   | '.';  :    /  /  ,.  | /  /`--'  /  /`--'  / 
;   | |`-'    ;  :   .'   '--'.     /|  ,   /|   :    |---' |   :    |  ,   ;  :   .'   '--'.     '--'.     /  
|   ;/        |  ,     .-./ `--'---'  ---`-'  \   \  /       \   \  / ---`-'|  ,     .-./ `--'---'  `--'---'   
'---'          `--`---'                        `----'         `----'         `--`---'                          
                                                                                                               
                                                        
                                                        _   _ 
                                                     __| | | |
                                                    / _` | | |
                                                    \__,_| |_|
                                                            
                                                                                                        
""")
