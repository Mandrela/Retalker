import os.path
import random
import sys
import time
import requests
import asyncio
import json

# from aioconsole import ainput

import logging
logging.getLogger('werkzeug')
logging.basicConfig(filename='retalker.log', filemode='at', format='%(asctime)s:%(levelname)s: %(message)s',
                    level=logging.DEBUG)


def output(*args, **kwargs) -> None:
    print(*args, **kwargs)


def get_input() -> str:
    return input()


def get_random(amount: int) -> list[str]:
    result: list[str] = []
    for _ in range(amount):
        word: str = ''
        for _ in range(random.randint(3, 8)):
            word += chr(random.randint(65, 90) + 32 * random.randint(0, 1))
        result.append(word)
    return result


def get_api(amount: int) -> list[str]:
    for _ in range(3):
        try:
            response: requests.Response = requests.get(f'https://random-word-api.herokuapp.com/word?number={amount}')
            if response.status_code == 200:
                return response.json()
            logging.warning(f'Failed to fetch words: {response.reason}({response.status_code})')
        except Exception as ex:
            logging.error(f'Caught an exception {ex = } {ex.__cause__ = }', stack_info=True)
    logging.error(f'Failed to fetch words: {amount = }')
    logging.info('Trying to use fallback')
    try:
        result = json.load(open('fallback.json', 'rt'))
    except FileNotFoundError:
        logging.critical('No fallback file')
        result = ['critical']
    random.shuffle(result)
    return result[:amount]


def get_wordlist(amount: int, name: str) -> list[str]:
    result: list[str] = json.load(open('dicts.json'))[name]
    random.shuffle(result)
    return result[:amount]


def add_dict(wordlist: list[str], name: str) -> None:
    if not os.path.exists('dicts.json'):
        obj = {}
    else:
        obj = json.load(open('dicts.json', 'rt'))
    obj[name.lower()] = wordlist
    json.dump(obj, open('dicts.json', 'wt'))
    logging.debug(f'Added wordlist "{name}"')


def del_dict(name: str) -> None:
    obj: dict = json.load(open('dicts.json', 'rt'))
    obj.pop(name)
    json.dump(obj, open('dicts.json', 'wt'))
    logging.debug(f'Deleted wordlist "{name}"')


def list_dict() -> list[str]:
    if not os.path.exists('dicts.json'):
        obj = {}
    else:
        obj = json.load(open('dicts.json', 'rt'))
    return list(obj.keys())


async def session(wordlist: list[str], difficulty: int = 3) -> int:  # TODO collecting analytic data
    output('\nRepeat words:')
    guessed_right: int = 0
    for word in wordlist:
        output('-- ' + word + ' --')
        # try:
        #     result = await asyncio.wait_for(ainput(), timeout=1 * len(word))
        # except asyncio.TimeoutError:
        #     result = None
        #     print("Time's out")

        start: float = time.time()
        result: str = get_input()
        if result == word and time.time() - start <= (1.2 * (len(word) - 1) ** 0.5 + 1) * difficulty + 1:
            guessed_right += 1
            output('Nice!')
        elif result == word:
            output('Too long!')
        else:
            output('Wrong!')
    return round(guessed_right / len(wordlist) * 100)


async def cli() -> None:
    print('Welcome to retalker command-line interface!')
    while (command := input('1. [S]tart\t2. [W]ordlists\t3. [E]xit\n>>> ').lower()) not in ['exit', 'e', '3']:
        if command in ['start', 's', '1']:
            difficulty: int = 0
            mode: str = ''
            while not difficulty:
                if (mode := input('Choose difficulty:\n1. [H]ard\t2. [N]ormal\t3. [E]asy\t4. [B]ack\n>>> ')
                        .lower()) in ['h', 'hard', '1']:
                    difficulty = 1
                elif mode in ['n', 'normal', '2']:
                    difficulty = 3
                elif mode in ['e', 'easy', '3']:
                    difficulty = 9
                elif mode in ['b', 'back', '4']:
                    break
            if mode in ['b', 'back', '4']:
                print()
                continue

            while not (amount := input('Amount of words:\n>>> ').lower()).isnumeric() or int(amount) <= 0:
                pass
            amount = int(amount)

            dictionary: list = []
            while not dictionary:
                if (mode := input('Choose mode:\n1. [D]ictionary\t2. Random [w]ords\t3. Random [l]etters\t4. '
                                  '[B]ack\n>>> ')
                        .lower()) in ['d', 'dictionary', '1']:
                    if not (list_of_dicts := list_dict()):
                        print('No dicts awailable')
                        continue
                    print('\n'.join([f'- {x}' for x in list_of_dicts]))
                    while (file_name := input("Choose dict by typing its' name:\n>>> ")) not in list_dict():
                        pass
                    dictionary = get_wordlist(amount, file_name)
                elif mode in ['w', 'words', '2']:
                    dictionary = get_api(amount)
                elif mode in ['l', 'letters', '3']:
                    dictionary = get_random(amount)
                elif mode in ['b', 'back', '4']:
                    break

            if dictionary and difficulty:
                a = await session(dictionary)
                print(f'Result: {a}%')
                time.sleep(2)
            else:
                print()
                continue
        elif command in ['wordlists', 'w', '2']:
            while (kley := input('1. [A]dd\t2. [D]elete\t3. [B]ack\n>>> ').strip().lower()) not in ['3', 'b', 'back']:
                if kley in ['a', 'add', '1']:
                    while not (name := input('Type name of file or "quit":\n>>> ').strip()) == 'quit':
                        try:
                            add_dict(json.load(open(name, 'rt')), name.split('.')[0])
                            break
                        except FileNotFoundError:
                            logging.error(f'File {name} not found')
                elif kley in ['d', 'delete', '2']:
                    if not list_dict():
                        print('No wordlists')
                        continue
                    print('\n'.join([f'- {x}' for x in list_dict()]))
                    while not (name := input('Type name of wordlist or "quit":\n>>> ').strip()) == 'quit':
                        if name in list_dict():
                            del_dict(name)
                            print('Success')
                            break
                        print('No such name')
            print()
    print('Goodbye!')


if not os.path.exists('fallback.json'):
    try:
        json.dump(requests.get('https://random-word-api.herokuapp.com/word?number=100').json(),
                  open('fallback.json', 'wt'))
    except Exception as ex:
        logging.critical(f'Fail while creating fallback: {ex = } {ex.__cause__ = }', stack_info=True)
        print('Failed to create a fallback file. Check logs for more info')
        sys.exit(1)
if __name__ == '__main__':
    asyncio.run(cli())
