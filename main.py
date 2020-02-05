import json
import os
import requests
from datetime import time


TOKEN = os.getenv('VK_TOKEN')
V = '5.103'


def vk(meth, params, timeout=10):
    method = {
        'get_user': 'users.get',
        'get_friends': 'friends.get',
        'get_groups': 'groups.get',
        'get_groupsById': 'groups.getById'
    }[meth]
    try:
        response = requests.get(
            f'https://api.vk.com/method/{method}',
            params,
            timeout=timeout
        )
    except requests.exceptions.ReadTimeout:
        print('Read timeout')
        return vk(meth, params, 20)

    print("-")
    data = response.json()

    if 'error' in data:
        if data['error']['error_code'] == 6:
            time.sleep(1)
            return vk(meth, params)
        else:
            return data['error']
    return data['response']


def write_json(data):
    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print('Результат записан в файл result.json')


class User:

    def __init__(self, user='0'):
        self.token = TOKEN
        params = self.get_params()
        params['user_ids'] = user
        response = vk('get_user', params)
        if 'error_code' not in response:
            response = response[0]
            self.user_id = response['id']
            self.first_name = response['first_name']
            self.last_name = response['last_name']

            if response.get('deactivated') == 'banned':
                raise Exception('Страница пользователя заблокировна')
            elif response.get('deactivated') == 'deleted':
                raise Exception('Страница пользователя удалена')

            if response['is_closed'] and not response['can_access_closed']:
                raise Exception('Профиль скрыт настройками приватности')
        else:
            raise Exception(response['error_msg'])

    def __repr__(self):
        return f'https://vk.com/id{self.user_id}'

    def get_params(self):
        return dict(
            access_token=self.token,
            v=V
        )

    def get_friends(self, user_id=''):
        if user_id == '':
            user_id = self.user_id
        params = self.get_params()
        params['user_id'] = user_id
        response = vk('get_friends', params)
        if 'error_code' not in response:
            return response['items']
        else:
            print(f"Не удалось получить друзей пользователя  https://vk.com/id{user_id} \
                  {response['error_msg']}")
            return []

    def get_groups(self, user_id=''):
        if user_id == '':
            user_id = self.user_id
        params = self.get_params()
        params['user_id'] = user_id
        response = vk('get_groups', params)
        if 'error_code' not in response:
            return response['items']
        else:
            print(f"Не удалось получить группы пользователя https://vk.com/id{user_id} \
                              {response['error_msg']}")
            return []

    def get_ind_groups(self):
        groups = set(self.get_groups()[0:1000])
        if groups:
            friends = self.get_friends()
            for friend in friends:
                friends_groups = set(self.get_groups(friend))
                groups.difference_update(friends_groups)

            result_list = []
            for group in groups:
                params = self.get_params()
                params['fields'] = 'members_count'
                params['group_id'] = group
                params['extended'] = 1
                response = vk('get_groupsById', params)
                if 'error_code' not in response:
                    response = response[0]
                    result = {
                        'name': response.get('name'),
                        'gid': response.get('id'),
                        'members_count': response.get('members_count')
                    }
                    result_list.append(result)
                else:
                    print(f"Не удалось получить информацию по группе {group} \
                            {response['error_msg']}")

            write_json(result_list)
            return result_list


if __name__ == '__main__':
    Evgeniy = User('eshmargunov')
    groups_user = Evgeniy.get_ind_groups()
