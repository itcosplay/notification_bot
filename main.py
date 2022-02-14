import os
import logging
import time
import requests

from environs import Env


def send_msg(text, token, chat_id):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }

    response = requests.get(url, params=payload)
    response.raise_for_status()


def main():
    logging.basicConfig(level=logging.INFO)

    env = Env()
    env.read_env()

    devman_token = os.environ['DEVMAN_TOKEN']
    bot_token = os.environ['BOT_TOKEN']
    chat_id = os.environ['CHAT_ID']

    url = 'https://dvmn.org/api/long_polling/'
    payload = None
    headers = {
        'Authorization': f'Token {devman_token}'
    }

    logging.info('Bot started')

    while True:
        try:
            response = requests.get(url, headers=headers, params=payload)
            response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            continue
        except ConnectionError:
            time.sleep(5)
            continue

        check_info = response.json()

        if check_info['status'] == 'timeout':
            payload = {
                'timestamp': check_info['timestamp_to_request']
            }
            continue

        for new_attempt in check_info['new_attempts']:
            conclusion_msg = {
                True: 'В вашей работе ошибка!',
                False: 'Все супер, едем дальше!'
            }
            success_msg = conclusion_msg[new_attempt['is_negative']]
            lesson_title = new_attempt['lesson_title']
            message = f'У вас проверили работу {lesson_title}\n\n{success_msg}'
            send_msg(message, bot_token, chat_id)

            payload = {
                'timestamp': check_info['last_attempt_timestamp']
            }


if __name__ == '__main__':
    main()
















