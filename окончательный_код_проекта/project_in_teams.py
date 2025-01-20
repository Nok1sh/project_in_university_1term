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
        self.__dishes: str = ''
        self.__recipe_dishes: str = ''
        self.keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Загрузить фото")],
                [KeyboardButton(text="Добавить продукты")],
                [KeyboardButton(text='Убрать продукт')],
                [KeyboardButton(text="Генерация")],
                [KeyboardButton(text="Рецепт")],
                [KeyboardButton(text="Информация")]
            ],
            resize_keyboard=True
        )
        self.keyboard_generation = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text='Да')],
                [KeyboardButton(text='Нет')]
            ],
            resize_keyboard=True
        )
        self.keyboard_dishes = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text='Суп')],
                [KeyboardButton(text='Салат')],
                [KeyboardButton(text='Основное блюдо')],
                [KeyboardButton(text='Свой вариант')]
            ],
            resize_keyboard=True
        )

    def __generate_bot(self, selected_dishes=None, category=None) -> None:
        if not selected_dishes:
            if not category:
                response = genbot.get_chat_completion(genbot.giga_token, f"напиши, пожалуйста, несколько блюд, которые можно приготовить из набора продуктов: {self.string_product}. Просто перечисли названия блюд. Используй такой шаблон для ответа: в начале напиши 'Вот несколько блюд, которые можно приготовить из предложенных продуктов', а дальше перечисляй, например, 1.**название блюда** и так далее с каждым блюдом")
                self.__dishes = response.json()['choices'][0]['message']['content']
                self.restart_string_product()
            else:
                response = genbot.get_chat_completion(genbot.giga_token,
                                                      f"напиши, пожалуйста, несколько блюд, которые можно приготовить из категории блюд: {category}, из набора продуктов: {self.string_product}. Просто перечисли названия блюд. Используй такой шаблон для ответа: в начале напиши 'Вот несколько блюд, которые можно приготовить из предложенных продуктов', а дальше перечисляй, например, 1.**название блюда** и так далее с каждым блюдом")
                self.__dishes = response.json()['choices'][0]['message']['content']
                self.restart_string_product()
        else:
            response = genbot.get_chat_completion(genbot.giga_token,f"напиши, пожалуйста рецепт {selected_dishes}. В начале напиши: 'Рецепт {selected_dishes}:'")
            self.__recipe_dishes = response.json()['choices'][0]['message']['content']

    def generate_dishes(self, category=None) -> str:
        self.__generate_bot(category=category)
        return self.__dishes

    def generate_recipe(self, user_message: int):
        selected_dishes: str = ''
        count_dishes: int = 0
        for dish in self.__dishes.split('\n'):
            if '**' in dish and dish.count('**') == 2:
                count_dishes += 1
                if count_dishes == user_message:
                    selected_dishes = dish[dish.find('**')+2:dish.rfind('**')]
                    break
        if count_dishes < user_message:
            return -1
        self.__generate_bot(selected_dishes=selected_dishes)
        return self.__recipe_dishes

    def forming_string_from_products(self) -> str:
        products: List[str] = list(detect.detect_object('test_photo.jpg'))
        if len(products) != 0:
            for product in products[:-1]:
                self.string_product += f'{product} '
            self.string_product += f'{products[-1]} '
        return self.string_product

    def add_products_in_string(self, message) -> None:
        new_products = ' '.join(message.split())
        self.string_product += new_products

    def del_product_in_string(self, message):
        self.string_product = self.string_product.replace(message, '')

    def check_existence_object(self, object: str) -> bool:
        if object == 'dishes':
            return bool(self.__dishes)
        return bool(self.string_product)

    def restart_string_product(self) -> None:
        self.string_product: str = ''


# дальше расписан сам бот

flag_generate: int = 0
flag_photo: int = 0
flag_recipe: int = 0
flag_add_product: int = 0
flag_del_product: int = 0
TOKEN = TelegramToken()
dp = Dispatcher()
bot = Bot(token=TOKEN)
Tools = ToolsAndFunction()


@dp.message(CommandStart())
async def command_start_handler(message: Message):
    Tools.restart_string_product()
    await message.answer(
            text="Привет! Выберите действие:",
            reply_markup=Tools.keyboard
        )


@dp.message(F.text == "Загрузить фото")
async def upload_photo_handler(message: Message):
    global flag_add_product, flag_recipe, flag_photo, flag_generate, flag_del_product
    flag_generate = flag_del_product = flag_recipe = flag_add_product = 0
    flag_photo = 1
    await message.answer("Отлично, отправьте мне фото ваших продуктов!")


@dp.message(F.text == "Генерация")
async def generate(message: Message):
    if Tools.check_existence_object('products'):
        await message.answer('Нужно ли выбрать категорию блюд', reply_markup=Tools.keyboard_generation)
    else:
        await message.answer('Вы ещё не добавили продукты')

# ----------------------------


@dp.message(F.text == "Да")
async def category_yes(message: Message):
    await message.answer('Пожалуйста выберите категорию блюд', reply_markup=Tools.keyboard_dishes)


# ----------------------------


@dp.message(F.text == 'Суп')
async def dishes_soap(message: Message):
    await message.answer(Tools.generate_dishes('суп'), reply_markup=Tools.keyboard)


@dp.message(F.text == 'Салат')
async def dishes_soap(message: Message):
    await message.answer(Tools.generate_dishes('салат'), reply_markup=Tools.keyboard)


@dp.message(F.text == 'Основное блюдо')
async def dishes_soap(message: Message):
    await message.answer(Tools.generate_dishes('основное блюдо'), reply_markup=Tools.keyboard)


@dp.message(F.text == 'Свой вариант')
async def dishes_soap(message: Message):
    global flag_add_product, flag_recipe, flag_photo, flag_generate, flag_del_product
    flag_photo = flag_del_product = flag_recipe = flag_add_product = 0
    flag_generate = 1
    await message.answer('Пожалуйста напишите категорию блюд')


# ----------------------------


@dp.message(F.text == "Нет")
async def category_no(message: Message):
    await message.answer(Tools.generate_dishes(), reply_markup=Tools.keyboard)


# ----------------------------

@dp.message(F.text == 'Добавить продукты')
async def add_products(message: Message):
    global flag_add_product, flag_recipe, flag_photo, flag_generate, flag_del_product
    flag_generate = flag_del_product = flag_recipe = flag_photo = 0
    flag_add_product = 1
    await message.answer('Добавьте продукты')


@dp.message(F.text == 'Убрать продукт')
async def del_product(message: Message):
    global flag_add_product, flag_recipe, flag_photo, flag_generate, flag_del_product
    flag_generate = flag_photo = flag_recipe = flag_add_product = 0
    flag_del_product = 1
    await message.answer('Выберите продукт для удаления')


@dp.message(F.text == "Информация")
async def information(message: Message):
    await message.answer("🍎Это кулинарный бот, способный предложить несколько блюд, из имеющихся продуктов\n\n🥝Добавлять блюда можно как с помощью фотографий продуктов, так и просто нажав кнопку 'Добавить продукт'\nПродукты, которые определяет бот:\n🥕морковь     🍆баклажан\n🥒огурец       🧀сыр\n🥔картошка   🥚яйцо\n🥓колбаса     🥛бутылка молока\n\n🍄Когда добавили все продукты, нужно нажать кнопку 'Генерация' и нажать 'Да', если нужна категория блюд, и 'Нет', если категория не нужна\n\n🍌Чтобы получить рецепт одного из сгенерированных блюд, нужно нажать кнопку 'Рецепт' и написать число, под которым находится выбранное блюдо")


@dp.message(F.text == "Рецепт")
async def recipe(message: Message):
    global flag_add_product, flag_recipe, flag_photo, flag_generate, flag_del_product
    flag_generate = flag_del_product = flag_photo = flag_add_product = 0
    if Tools.check_existence_object('dishes'):
        flag_recipe = 1
        await message.answer('Напишите число, под которым находится блюдо, для которого нужен рецепт')
    else:
        await message.answer('Вы ещё не сгенерировали блюда')
        flag_recipe = 0


@dp.message()
async def interaction_with_the_bot(message: Message):
    global flag_add_product, flag_recipe, flag_photo, flag_generate, flag_del_product
    if flag_add_product == 1:  # часть кода для добавления продуктов
        if message.text not in ['Рецепт', 'Добавить продукты', 'Загрузить фото', 'Убрать продукт', 'Генерация', 'Информация']:
            Tools.add_products_in_string(message.text)
            await message.answer(f'Ваши продукты:\n{Tools.string_product}')
        flag_add_product = 0
    if flag_recipe == 1:  # часть кода для получения номера блюда для получения рецепта
        if message not in ['Рецепт', 'Добавить продукты', 'Загрузить фото', 'Убрать продукт', 'Генерация',
                           'Информация']:
            user_message = message.text
            if any(number not in '0123456789' for number in str(user_message)) or int(user_message) <= 0:
                await message.answer('Вы указали неверное значение')
            else:
                recipe_selected_dishes = Tools.generate_recipe(int(user_message))
                if recipe_selected_dishes == -1:
                    await message.answer('Вы указали неверное значение')
                else:
                    await message.answer(recipe_selected_dishes)
        flag_recipe = 0
    if flag_photo == 1:  # часть кода для обработки отправленного фото
        if message not in ['Рецепт', 'Добавить продукты', 'Загрузить фото', 'Убрать продукт', 'Генерация',
                           'Информация']:
            await message.bot.download(file=message.photo[-1].file_id, destination='test_photo.jpg')
            await message.answer(f"Ваши продукты:\n{Tools.forming_string_from_products()}")

        flag_photo = 0
    if flag_generate == 1:  # часть кода для получения категории блюда
        if message not in ['Рецепт', 'Добавить продукты', 'Загрузить фото', 'Убрать продукт', 'Генерация',
                           'Информация']:
            await message.answer(Tools.generate_dishes(message), reply_markup=Tools.keyboard)
        flag_generate = 0
    if flag_del_product == 1:  # часть кода для удаления продукта
        if message not in ['Рецепт', 'Добавить продукты', 'Загрузить фото', 'Убрать продукт', 'Генерация',
                           'Информация']:
            if message.text not in Tools.string_product:
                await message.answer('Такого продукта нет')
            else:
                Tools.del_product_in_string(message.text)
                await message.answer(f'Ваши продукты:\n{Tools.string_product}')
        flag_del_product = 0


async def main() -> None:
    await dp.start_polling(bot)
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
asyncio.run(main())



