import math
import random
import time
import asyncio

# from aioconsole import ainput


async def session(wordlist: list[str], difficulty: int = 3) -> int:  # TODO collecting analytic data
    print('\nRepeat words:')
    guessed_right: int = 0
    for word in wordlist:
        print('\t' + word)
        # try:
        #     result = await asyncio.wait_for(ainput(), timeout=1 * len(word))
        # except asyncio.TimeoutError:
        #     result = None
        #     print("Time's out")

        start: float = time.time()
        result: str = input()
        if result == word and time.time() - start <= len(word) * difficulty + 1:
            guessed_right += 1
            print('Nice!')
        elif result == word:
            print('Too long!')
        else:
            print('Wrong!')
    return round(guessed_right / len(wordlist) * 100)


async def cli() -> None:
    print('Welcome to retalker command-line interface!')
    while (command := input('1. [S]tart\t2. [W]ordlists\t3. [E]xit\n>>> ').lower()) not in ['exit', 'e', '3']:
        if command in ['start', 's', '1']:
            dictionary: list = []
            while not dictionary:
                if (mode := input('Choose mode:\n1. [D]ictionary\t2. Random [w]ords\t3. Random [l]etters\t4. '
                                  '[B]ack\n>>> ')
                        .lower()) in ['d', 'dictionary', '1']:
                    dictionary = ['1']  # TODO dict mode
                elif mode in ['w', 'words', '2']:
                    dictionary = ['2']  # TODO api mode
                elif mode in ['l', 'letters', '3']:
                    dictionary = ['3']  # TODO full random mode
                elif mode in ['b', 'back', '4']:
                    break

            difficulty: int = 0
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

            if dictionary and difficulty:
                a = await session(dictionary)
                print(f'Result: {a}%')
                time.sleep(1)
            else:
                print()
                continue
        elif command in ['wordlists', 'w', '2']:
            print('placeholder 1')
    print('Goodbye!')


if __name__ == '__main__':
    # dictionary: list = ['string']  # file.json <- {'dict_name': ['string',...]}
    # load from file or use api
    asyncio.run(cli())
