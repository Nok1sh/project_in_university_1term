import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.types import Message
from typing import List
from NeuralNetwork import GigaChatBot as genbot
from NeuralNetwork import DetectYolo as detect
from TOKENSFILE import TelegramToken

class ToolsAndFunction:

    def __init__(self):
        self.string_product: str = ''
        self.dishes: str = ''
        self.recipe_dishes: str = ''
        self.__keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Загрузить фото")],
                [KeyboardButton(text="Добавить продукты")],
                [KeyboardButton(text="Генерация")],
                [KeyboardButton(text="Рецепт")],
                [KeyboardButton(text="Информация")]
            ],
            resize_keyboard=True
        )
    def generate_bot(self, selected_dishes=None) -> None:
        conversation_history = []
        if selected_dishes == None:
            response, conversation_history = genbot.get_chat_completion(genbot.giga_token, f"напиши, пожалуйста, несколько блюд, которые можно приготовить из набора продуктов: {self.string_product}. Просто перечисли названия блюд. Используй такой шаблон для ответа: в начале напиши 'Вот несколько блюд, которые можно приготовить из предложенных продуктов', а дальше перечисляй, например, 1.**название блюда** и так далее с каждым блюдом", conversation_history)
            self.dishes = conversation_history[1]['content']
            self.string_product: str = ''
        else:
            response, conversation_history = genbot.get_chat_completion(genbot.giga_token,f"напиши, пожалуйста рецепт {selected_dishes}. В начале напиши: 'Рецепт {selected_dishes}:'",conversation_history)
            self.recipe_dishes = conversation_history[1]['content']

    def detect_product(self, image: str) -> str:
        return detect.YOLODetectObject(image)

    def generate_dishes(self) -> str:
        self.generate_bot()
        return self.dishes

    def generate_recipe(self, user_message: int) -> str:
        selected_dishes: str = ''
        count_dishes: int = 0
        for dish in self.dishes.split('\n'):
            if '**' in dish and dish.count('**') == 2:
                count_dishes += 1
                if count_dishes == user_message:
                    selected_dishes = dish[dish.find('**')+2:dish.rfind('**')]
        if count_dishes < user_message:
            return -1
        self.generate_bot(selected_dishes=selected_dishes)
        return self.recipe_dishes

    def start_work(self, message) -> None:
        self.string_product: str = ''
        return message.answer(
            text="Привет! Выберите действие:",
            reply_markup=self.__keyboard
        )
    def forming_string_from_products(self) -> str:
        products: List[str] = list(Bot.detect_product('test_photo.jpg'))
        for product in products[:-1]:
            self.string_product += f'{product}, '
        self.string_product += f'{products[-1]} '
        return self.string_product

    def add_products_in_string(self, message) -> None:
        new_products = ' '.join(message.split())
        self.string_product += new_products

# дальше расписан сам бот

flag_photo: int = 0
flag_recipe: int = 0
flag_add_product: int = 0
TOKEN = TelegramToken()
dp = Dispatcher()
bot = Bot(token=TOKEN)
Bot = ToolsAndFunction()
@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await Bot.start_work(message)

@dp.message(F.text == "Загрузить фото")
async def upload_photo_handler(message: Message):
    global flag_photo
    flag_photo = 1
    await message.answer("Отлично, отправьте мне фото ваших продуктов!")

@dp.message(F.text == "Генерация")
async def generate(message: Message):
    if Bot.string_product != '':
        await message.answer(Bot.generate_dishes())
    else:
        await message.answer('Вы ещё не добавили продукты')
@dp.message(F.text == 'Добавить продукты')
async def add_products(message: Message):
    global flag_add_product
    flag_add_product = 1
    await message.answer('Добавьте продукты')
@dp.message(F.text == "Информация")
async def information(message: Message):
    await message.answer("🍎Это кулинарный бот, способный предложить несколько блюд, из имеющихся продуктов\n\n🥕Добавлять блюда можно как с помощью фотографий продуктов, так и просто нажав кнопку 'Добавить продукт'\n\n🍄Когда добавили все продукты, нужно нажать кнопку 'Генерация'\n\n🍌Чтобы получить рецепт одного из сгенерированных блюд, нужно нажать кнопку 'Рецепт' и написать число, под которым находится выбранное блюдо")

@dp.message(F.text == "Рецепт")
async def recipe(message: Message):
    global flag_recipe
    if Bot.dishes != '':
        flag_recipe = 1
        await message.answer('Напишите число, под которым находится блюдо, для которого нужен рецепт')
    else:
        await message.answer('Вы ещё не сгенерировали блюда')
        flag_recipe = 0

@dp.message()
async def interaction_with_the_bot(message: Message):
    global flag_add_product, flag_recipe, flag_photo
    if flag_add_product == 1: # часть кода для добавления продуктов
        Bot.add_products_in_string(message.text)
        await message.answer(f'Ваши продукты:\n{Bot.string_product}')
        flag_add_product = 0
    if flag_recipe == 1: # часть кода для получения номера блюда для получения рецепта
        user_message = message.text
        if any(number not in '0123456789' for number in str(user_message)) or int(user_message) <= 0:
            await message.answer('Вы указали неверное значение')
        else:
            recipe_selected_dishes = Bot.generate_recipe(int(user_message))
            if recipe_selected_dishes == -1:
                await message.answer('Вы указали неверное значение')
            else:
                await message.answer(recipe_selected_dishes)
        flag_recipe = 0
    if flag_photo == 1: # часть кода для обработки отправленного фото
        await message.bot.download(file=message.photo[-1].file_id, destination='test_photo.jpg')
        flag_photo = 0
        await message.answer(f"Ваши продукты:\n{Bot.forming_string_from_products()}")

# запускает бота
async def main() -> None:
    await dp.start_polling(bot)
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
asyncio.run(main())



