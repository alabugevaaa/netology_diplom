import json
import os
import requests
import time
import math


TOKEN = os.getenv('VK_TOKEN')
V = '5.103'


def vk(meth, id, params, timeout=10):
    code = {
        'get_user': 'return API.users.get({"user_ids": "' + str(id) + '"});',
        'get_friends': 'return API.friends.get({"user_id": "' + str(id) + '"});',
        'get_groups': 'return API.groups.get({"user_id": "' + str(id) + '"});',
        'get_groupsById': 'return API.groups.getById({"group_id": "' + str(id) + '", \
            "extended": "1", "fields": "members_count"});'
    }[meth]
    params['code'] = code
    try:
        response = requests.get(
            f'https://api.vk.com/method/execute',
            params,
            timeout=timeout
        )
    except requests.exceptions.ReadTimeout:
        print('Read timeout')
        return vk(meth, id, params, 20)

    data = response.json()

    if 'error' in data:
        if data['error']['error_code'] == 6:
            time.sleep(1)
            return vk(meth, id, params)
        else:
            return data['error']
    return data['response']


def write_json(data):
    print('\rЗапись в файл...', end='')
    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print('\rРезультат записан в файл result.json', end='')

def print_progress(bar_len, count, i):
    d = math.floor(bar_len / count * (i + 1))
    text = '\r|{0}{1}|'.format('#' * d, '-' * (bar_len - d))
    print(text, f"Осталось обработать {count - i} друзей", end='')
    return text


class User:

    def __init__(self, user='0'):
        self.token = TOKEN
        response = vk('get_user', user, self.get_params())
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
        response = vk('get_friends', user_id, self.get_params())
        if 'error_code' not in response:
            return response['items']
        else:
            return []

    def get_groups(self, user_id=''):
        if user_id == '':
            user_id = self.user_id
        response = vk('get_groups', user_id, self.get_params())
        if 'error_code' not in response:
            return response['items']
        else:
            return []

    def get_ind_groups(self, n=5):
        groups = set(self.get_groups()[0:1000])
        set_group = groups
        common_groups = {}
        if groups:
            friends = self.get_friends()
            i = 0
            for friend in friends:
                friends_groups = set(self.get_groups(friend))
                inter_groups = groups & friends_groups
                for inter_group in inter_groups:
                    current_gr = common_groups.get(inter_group)
                    if current_gr is None:
                        common_groups[inter_group] = 1
                    else:
                        common_groups[inter_group] += 1

                set_group.difference_update(friends_groups)
                for key, value in common_groups.items():
                    if value < n:
                        set_group.add(key)

                text = print_progress(50, len(friends), i)
                i += 1
            print(text + " Список групп получен")

            result_list = []
            print('\rПолучение информации о группах...', end='')
            for group in set_group:
                response = vk('get_groupsById', group, self.get_params())
                if 'error_code' not in response:
                    response = response[0]
                    result = {
                        'name': response.get('name'),
                        'gid': response.get('id'),
                        'members_count': response.get('members_count')
                    }
                    result_list.append(result)

            write_json(result_list)
            return result_list


if __name__ == '__main__':
    Evgeniy = User('eshmargunov')
    groups_user = Evgeniy.get_ind_groups(5)
