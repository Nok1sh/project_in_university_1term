import requests
import uuid
import json
from tkinter import *
def chatBot(product):
    auth = 'MjYyMWExOTItN2IyMy00NDJkLWJlZmUtZjMxNDIxY2NkM2ZkOjNmNTRkMWQ3LWM2ZGQtNDE0Zi1hM2Q0LTBhODk5NWZmMjVkMQ=='

    def get_token(auth_token, scope='GIGACHAT_API_PERS'):
        """
          Выполняет POST-запрос к эндпоинту, который выдает токен.

          Параметры:
          - auth_token (str): токен авторизации, необходимый для запроса.
          - область (str): область действия запроса API. По умолчанию — «GIGACHAT_API_PERS».

          Возвращает:
          - ответ API, где токен и срок его "годности".
          """
        # Создадим идентификатор UUID (36 знаков)
        rq_uid = str(uuid.uuid4())

        # API URL
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

        # Заголовки
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': rq_uid,
            'Authorization': f'Basic {auth_token}'
        }

        # Тело запроса
        payload = {
            'scope': scope
        }

        try:
            # Делаем POST запрос с отключенной SSL верификацией
            # (можно скачать сертификаты Минцифры, тогда отключать проверку не надо)
            response = requests.post(url, headers=headers, data=payload, verify=False)
            return response
        except requests.RequestException as e:
            print(f"Ошибка: {str(e)}")
            return -1

    response = get_token(auth)
    if response != 1:
        print(response.text)
        giga_token = response.json()['access_token']

    def get_chat_completion(auth_token, user_message, conversation_history=None):
        """
        Отправляет POST-запрос к API чата для получения ответа от модели GigaChat в рамках диалога.

        Параметры:
        - auth_token (str): Токен для авторизации в API.
        - user_message (str): Сообщение от пользователя, для которого нужно получить ответ.
        - conversation_history (list): История диалога в виде списка сообщений (опционально).

        Возвращает:
        - response (requests.Response): Ответ от API.
        - conversation_history (list): Обновленная история диалога.
        """
        # URL API, к которому мы обращаемся
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

        # Если история диалога не предоставлена, инициализируем пустым списком
        if conversation_history is None:
            conversation_history = []

        # Добавляем сообщение пользователя в историю диалога
        conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Подготовка данных запроса в формате JSON
        payload = json.dumps({
            "model": "GigaChat:latest",
            "messages": conversation_history,
            "temperature": 1,
            "top_p": 0.1,
            "n": 1,
            "stream": False,
            "max_tokens": 512,
            "repetition_penalty": 1,
            "update_interval": 0
        })

        # Заголовки запроса
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {auth_token}'
        }

        # Выполнение POST-запроса и возвращение ответа
        try:
            response = requests.post(url, headers=headers, data=payload, verify=False)
            response_data = response.json()
            print(response_data)

            # Добавляем ответ модели в историю диалога
            conversation_history.append({
                "role": "assistant",
                "content": response_data['choices'][0]['message']['content']
            })

            return response, conversation_history
        except requests.RequestException as e:
            # Обработка исключения в случае ошибки запроса
            print(f"Произошла ошибка: {str(e)}")
            return None, conversation_history


    # Пример использования функции для диалога

    conversation_history = []

    # Пользователь отправляет первое сообщение
    response, conversation_history = get_chat_completion(giga_token, "какие блюда можно приготовить из продуктов: куринное филе, сыр, майонез, яйца, лук, помидоры", conversation_history)
    return conversation_history
text = [{'role': 'user', 'content': 'какие блюда можно приготовить из продуктов: куринное филе, сыр, майонез, яйца, лук, помидоры'}, {'role': 'assistant', 'content': 'Из перечисленных продуктов можно приготовить множество вкусных блюд. Вот несколько идей:\n\n1. **Салат с курицей и сыром**:\n   - Куриное филе отварить и нарезать кубиками.\n   - Сыр натереть на крупной терке.\n   - Лук и помидоры нарезать кубиками.\n   - Все ингредиенты смешать, добавить майонез и перемешать.\n\n2. **Куриные грудки с сыром и помидорами**:\n   - Куриные грудки отбить, посолить и поперчить.\n   - На каждую грудку выложить ломтик сыра и кружочек помидора.\n   - Завернуть грудки в фольгу и запечь в духовке при 180°C около 30 минут.\n\n3. **Запеканка с курицей и сыром**:\n   - Куриное филе отварить и нарезать кубиками.\n   - Лук и помидоры нарезать кубиками.\n   - Яйца взбить с майонезом.\n   - В форму для запекания выложить слоями курицу, лук, помидоры и сыр.\n   - Залить все взбитыми яйцами с майонезом.\n   - Запекать в духовке при 180°C около 30 минут.\n\n4. **Куриные рулетики с сыром и луком**:\n   - Куриное филе отбить, посолить и поперчить.\n   - Лук нарезать полукольцами и обжарить до золотистого цвета.\n   - На каждое филе выложить ломтик сыра и обжаренный лук.\n   - Свернуть филе рулетиком и закрепить зубочисткой.\n   - Обжарить рулетики на сковороде до золотистой корочки.\n   - Запечь в духовке при 180°C около 15 минут.\n\n5. **Салат с курицей, сыром и яйцами**:\n   - Куриное филе отварить и нарезать кубиками.\n   - Сыр натереть'}]
window = Tk()
window.geometry('700x700')
label = Label(text=text[1]['content'])
label.place(x=10, y=5, width=650, height=650)
window.mainloop()



