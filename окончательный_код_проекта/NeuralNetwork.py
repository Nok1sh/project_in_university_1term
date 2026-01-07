import uuid
import requests
import json
import os
from typing import Dict, Set
from ultralytics import YOLO
from googletrans import Translator
from TOKENSFILE import GigaChatToken # возьмёте свой токен и уберёте это
class GigaChatBot:
    auth = GigaChatToken()  # а сюда вставите свой токен вместо GigaChatToken()
    def get_token(auth_token, scope='GIGACHAT_API_PERS'):
        rq_uid = str(uuid.uuid4())
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': rq_uid,
            'Authorization': f'Basic {auth_token}'
        }
        payload = {
            'scope': scope
        }
        try:
            response = requests.post(url, headers=headers, data=payload, verify=False)
            return response
        except requests.RequestException as e:
            return -1

    response = get_token(auth)
    if response != 1:
        giga_token = response.json()['access_token']
    def get_chat_completion(auth_token, user_message, conversation_history=None):
        if conversation_history is None:
            conversation_history = []
        conversation_history.append({
            "role": "user",
            "content": user_message
        })
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
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
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {auth_token}'
        }
        try:
            response = requests.post(url, headers=headers, data=payload, verify=False)
            response_data = response.json()

            conversation_history.append({
                "role": "assistant",
                "content": response_data['choices'][0]['message']['content']
            })

            return response, conversation_history
        except requests.RequestException as e:
            return None, conversation_history

class DetectYolo:
    def YOLODetectObject(image: str):
        model = YOLO('best.pt')
        file_path: str = image
        results = model.predict(file_path, imgsz=640, conf=0.1)
        products: Dict[int, str] = {0: 'carrot', 1: 'cheese', 2: 'cucumber', 3: 'egg', 4: 'eggplant', 5: 'milk',
                                    6: 'potato', 7: 'sausage', 8: 'tomato'}
        try:
            os.remove('result_txt.txt')
        except:
            pass
        for result in results:
            result.save(filename="result.jpg")
            result.save_txt('result_txt.txt')
        translator = Translator()
        products_result: Set[str] = set()
        file_txt = open('result_txt.txt').readlines()
        for string in file_txt:
            translate_product = translator.translate(products[int(string[0])], src='en', dest='ru')
            products_result.add(translate_product.text)
        return products_result
