import os
import logging
import time
import requests
import telegram

from environs import Env


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def main():
    env = Env()
    env.read_env()

    devman_token = os.environ['DEVMAN_TOKEN']
    bot_token = os.environ['BOT_TOKEN']
    chat_id = os.environ['CHAT_ID']

    bot = telegram.Bot(token=bot_token)

    logger = logging.getLogger(__file__)
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(bot, chat_id))

    url = 'https://dvmn.org/api/long_polling/'
    payload = None
    headers = {
        'Authorization': f'Token {devman_token}'
    }

    logger.info('Bot started')

    while True:
        try:
            response = requests.get(url, headers=headers, params=payload)
            response.raise_for_status()

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
                logger.info(message)

                payload = {
                    'timestamp': check_info['last_attempt_timestamp']
                }
        
        except requests.exceptions.ReadTimeout as error:
            logger.error(error, exc_info=True)
            continue

        except ConnectionError as error:
            logger.error(error, exc_info=True)
            time.sleep(5)
            continue

        except Exception as error:
            logger.error(error, exc_info=True)
            time.sleep(5)


if __name__ == '__main__':
    main()
















