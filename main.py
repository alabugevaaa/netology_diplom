import json
import os
import requests
from pprint import pprint


TOKEN = os.getenv('VK_TOKEN')


class User:
    def __init__(self, user_id='0'):
        self.token = TOKEN
        self.user_id = user_id

    def __repr__(self):
        return f'https://vk.com/id{self.user_id}'

    def get_params(self):
        return dict(
            access_token=self.token,
            v='5.95'
        )

    def get_friends(self, user_id=''):
        if user_id == '':
            user_id = self.user_id
        params = self.get_params()
        params['user_id'] = user_id
        response = requests.get(
            'https://api.vk.com/method/friends.get',
            params
        )
        print("-")
        try:
            return response.json()['response']['items']
        except:
            print(f"Не удалось получить друзей пользователя https://vk.com/id{user_id} {response.json()['error']['error_msg']}")
            return []

    def get_groups(self, user_id=''):
        if user_id == '':
            user_id = self.user_id
        params = self.get_params()
        params['user_id'] = user_id
        response = requests.get(
            'https://api.vk.com/method/groups.get',
            params
        )
        print("-")
        try:
            return response.json()['response']['items']
        except:
            print(f"Не удалось получить группы пользователя https://vk.com/id{user_id} {response.json()['error']['error_msg']}")
            return []

    def get_ind_groups(self):
        groups = set(self.get_groups())
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
            response = requests.get(
                'https://api.vk.com/method/groups.getById',
                params
            )
            print("-")
            try:
                response = response.json()['response'][0]
                result = {
                    'name': response['name'],
                    'gid': response['id'],
                    'members_count': response['members_count']
                }
                result_list.append(result)
            except:
                print(f"Не удалось получить информацию по группе {group} {response.json()['error']['error_msg']}")


        with open('result.json', 'w', encoding='utf-8') as f:
            json.dump(result_list, f,  ensure_ascii=False, indent=2)

        return result_list



Evgeniy = User('171691064')
groups = Evgeniy.get_ind_groups()

print(groups)
