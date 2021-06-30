import logging
import aiohttp

from aiogram import Bot, Dispatcher, executor, types
import aiogram.utils.markdown as markdown

try:
    import settings
except ImportError:
    exit('DO cp settings.py.default settings.py and set token!')

# Сайт с АПИ Breaking Bad
URL = 'https://www.breakingbadapi.com/api/'

# Объект бота
bot = Bot(token=settings.token)
# Диспетчер для бота
dp = Dispatcher(bot)

# Включаем логирование
logging.basicConfig(level=logging.INFO)


# регулярные выражения для замены некорректных символов в имени
# pattern_incorrect = re.compile(r' |&|-|\.')

async def parser(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.json()
            return html


async def hero_information(message, hero):
    await message.answer(markdown.text(
        markdown.text(markdown.hunderline('Name: ', hero['name'])),
        markdown.text("Birthday: ", hero['birthday']),
        markdown.text("Occupation: ", ', '.join(hero['occupation'])),
        markdown.text("Img: ", hero['img']),
        markdown.text("Status: ", hero['status']),
        markdown.text("Nickname: ", hero['nickname']),
        markdown.text("Appearance: ", hero['appearance']),
        markdown.text("Portrayed: ", hero['portrayed']),
        sep="\n"
    ), parse_mode="HTML")


async def season_information(message, season):
    await message.answer(markdown.text(
        markdown.text(markdown.hunderline('Season: ', season['season'])),
        markdown.text("Title: ", season['title']),
        markdown.text("Episode: ", season['episode']),
        markdown.text("Characters: ", ', '.join(season['characters'])),
        markdown.text("Air_date: ", season['air_date']),
        sep="\n"
    ), parse_mode="HTML")


async def quote_information(message, quote):
    await message.answer(markdown.text(
        markdown.text(markdown.hunderline('Author: ', quote['author'])),
        markdown.text("Quote: ", quote['quote']),
        sep="\n"
    ), parse_mode="HTML")


async def death_information(message, death):
    await message.answer(markdown.text(
        markdown.text(markdown.hunderline('Death: ', death['death'])),
        markdown.text("Cause: ", death['cause']),
        markdown.text("Responsible: ", death['responsible']),
        markdown.text("Last_words: ", death['last_words']),
        markdown.text("Season: ", death['season']),
        markdown.text("Episode: ", death['episode']),
        markdown.text("Number of deaths: ", death['number_of_deaths']),
        sep="\n"
    ), parse_mode="HTML")


# Хэндлер на команду /help /start
@dp.message_handler(commands=['start', 'help'])
async def usual_answers(message: types.Message):
    await message.answer("I can tell you about the heroes, season of the TV series breaking bad. "
                         "If you want to know what exactly I can write, write /canDo")


@dp.message_handler(commands="canDo")
async def can_do(message: types.Message):
    answer = await parser(URL)
    await message.answer(
        f'I can tell you about - /{", /".join([_.replace("episodes", "season") for _ in answer.keys()])}')


@dp.message_handler(commands="characters")
async def characters(message: types.Message):
    list_hero = await parser(URL + 'characters')
    if message.text[12:] in [hero['name'] for hero in list_hero]:
        for hero in list_hero:
            if message.text[12:] == hero['name']:
                await hero_information(message, hero)
    else:
        answer = []
        for hero in list_hero:
            answer.append(hero['name'])
        await message.answer(
            f'Choose a character /allHero (you can write /random to select a random character) or look '
            f'at all of them {", ".join(answer)}\n Example: /characters Jesse Pinkman ')


@dp.message_handler(commands="allHero")
async def allHero(message: types.Message):
    list_hero = await parser(URL + 'characters')
    for hero in list_hero:
        await hero_information(message, hero)


@dp.message_handler(commands='random')
async def random(message: types.Message):
    hero = await parser(URL + 'character/random')
    await hero_information(message, hero[0])


@dp.message_handler(commands='quotes')
async def quotes(message: types.Message):
    quotes = await parser(URL + 'quotes')
    if message.text[8:] in [quote['author'] for quote in quotes]:
        for quote in quotes:
            if quote['author'] == message.text[8:] and quote['series'] == 'Breaking Bad':
                await quote_information(message, quote)
    else:
        answer = set()
        for quote in quotes:
            answer.add(quote['author'])
        await message.answer(f'You can choose a character and I will send you all his quotes {", ".join(answer)}'
                             f'\n Example: /quotes Jesse Pinkman ')


@dp.message_handler(commands='deaths')
async def deaths(message: types.Message):
    deaths = await parser(URL + 'deaths')
    if message.text[8:] in [death['death'] for death in deaths]:
        for death in deaths:
            if death['death'] == message.text[8:]:
                await death_information(message, death)
    else:
        answer = []
        for death in deaths:
            answer.append(death['death'])
        await message.answer(f'You can choose a character and I will send you his death {", ".join(answer)}'
                             f'\n Example: /deaths Rival Dealers ')


@dp.message_handler(commands=['season', 'season1', 'season2', 'season3', 'season4', 'season5'])
async def season(message: types.Message):
    number_season = message.text[-1:]
    if message.text == '/season':
        await message.answer(f'You can choose any season from 1 to 5 (but no more than one) and view information '
                             f'about it. To do this, write the /season(season number), for example, /season2')
    if number_season in [str(_) for _ in range(1, 5)]:
        seasons = await parser(URL + 'episodes')
        for episode in seasons:
            if episode['season'] == number_season and episode['series'] == 'Breaking Bad':
                await season_information(message, episode)


@dp.message_handler()
async def error_answer(message: types.Message):
    await message.answer(f'Maybe you made a mistake somewhere, try again')


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)

