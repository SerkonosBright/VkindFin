import vk_config
import requests
import vk_models
from vk_models import Session

class VKTools:

    def __init__(self):
        self.vkapi = vk_config.access_token
        self.params = {
            'access_token': self.vkapi,
            'v': vk_config.vkapi_version
        }
        self.offset = 0
        self.wish_list = []
        self.black_list = []

    def get_profile_info(self, user_id):

        endpoint = f'{vk_config.base_url}users.get'
        params = {
            'user_ids': user_id,
            'fields': 'first_name,'
                      'last_name,'
                      'bdate,'
                      'sex,'
                      'city,'
                      'relation'
        }
        try:
            response = requests.get(url=endpoint,
                                    params={**params,
                                            **self.params})

            if response.status_code != 200:
                raise ConnectionError

        except ConnectionError:
            print('Ошибка соединения!')

        else:
            data = response.json()['response'][0]

            first_name = data.get('first_name')
            last_name = data.get('last_name')
            name = f"{first_name} {last_name}"
            if not name:
                name = data.get('last_name')

        sex = (1, 2)[data.get('sex') == 1]

        bdate = data.get('bdate')
        if len(bdate) > 6:
            bdate = int(bdate[-4:])
        else:
            bdate = None

        relation = data.get('relation')

        if data.get('city'):
            city = data.get('city').get('title')
        else:
            city = None

        return name, sex, bdate, relation, city


def search_users(self, sex, bdate, relation, city, count=10):
    endpoint = f'{vk_config.base_url}users.search'

    session = Session()

    params = {
        'sex': sex,
        'bdate': bdate,
        'hometown': city,
        'relation': relation,
        'count': count,
        'has_photo': 1,
        'offset': self.offset
    }

    resp = requests.get(url=endpoint, params={**params,
                                              **self.params})

    if resp.json().get('error'):
        resp_error = resp.json()['error']['error_code'], \
            resp.json()['error']['error_msg']
        error_msg = f'Код ошибки: {resp_error[0]}\n' \
                    f'Сообщение об ошибке: {resp_error[1]}'
        print(error_msg)
        return 'Ошибка'

    for row in resp.json()['response']['items']:
        self.offset += 1

        if row['is_closed']:
            continue

        if session.query(
                vk_models.BlackList.vk_user_id) \
                .filter_by(vk_user_id=row['id']) \
                .first() is not None:
            continue

        if session.query(
                vk_models.FavoriteUser.vk_user_id) \
                .filter_by(vk_user_id=row['id']) \
                .first() is not None:
            continue

        photo_profile = self.get_photos(row['id'])

        return f'{vk_config.base_profile_url}{row["id"]}', \
            photo_profile


def get_photos(self, user_id):
    res = []

    endpoint = f'{vk_config.base_url}photos.get'
    params = {'owner_id': user_id,
              'album_id': 'profile',
              'extended': 1, }

    try:
        resp = requests.get(endpoint, params={**self.params,
                                              **self.params,
                                              **params})
        resp.raise_for_status()

        if resp.status_code != 200:
            raise ConnectionError

    except ConnectionError:
        print('Ошибка соединения!')

    else:
        like_score = 1
        comm_score = 3

        photos_sort = \
            lambda x: (x['likes']['count'], x['comments']['count']
                       )[x['likes']['count'] * like_score <=
                         x['comments']['count'] * comm_score]

        result = sorted(resp.json()['response']['items'],
                        key=photos_sort, reverse=True)

        for photo in result:
            res.append(f"photo{photo['owner_id']}_{photo['id']}")
            if len(res) == 3:
                break

        return ','.join(res)