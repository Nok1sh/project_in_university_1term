import asyncio
import logging
import sys
from os import getenv
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ContentType, FSInputFile
from ultralytics import YOLO
from googletrans import Translator
import os


def detect(image):
    model = YOLO('weights/best.pt')
    file_path = image
    results = model.predict(file_path, imgsz=640, conf=0.1)
    products = {1: 'cheese', 6: 'sausage', 7: 'tomato', 8: 'banana', 2: 'cucumber', 0:'carrot', 3:'egg', 4:'milk', 5:'potato'}
    try:
        os.remove('result_txt.txt')
    except:
        pass
    for result in results:
        result.save(filename="result.jpg")
        result.save_txt('result_txt.txt')

    translator = Translator()
    products_result = set()
    file_txt = open('result_txt.txt').readlines()
    for i in file_txt:
        translate_product = translator.translate(products[int(i[0])], src='en', dest='ru')
        products_result.add(translate_product.text)
    print(products_result)
    return products_result

TOKEN = '7572423155:AAG_9aYLKolLTdXlND9ibGLiDHJNEAq8XDw'

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, я кулинарный бот")


@dp.message(F.photo)
async def photo_img(message: Message) -> None:
    flag = 1
    await message.bot.download(file=message.photo[-1].file_id, destination='test_photo.jpg')

@dp.message(Command('image'))
async def test_net(message: Message):
    products = detect('test_photo.jpg')
    await message.answer(f'{products}')

async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
