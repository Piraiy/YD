from pprint import pprint
import json
import requests
from tqdm import tqdm


# Создаем класс для работы с фотографиями в ВК
class VkPhotos:
    url_metod = "https://api.vk.com/method/photos.get"
    def __init__(self, access_token, owner_id, url=url_metod,  v="5.131", album_id="profile", extended="1", count="5" ):
        self.access_token = access_token
        self.url = url
        self.v = v
        self.owner_id = str(owner_id)
        self.album_id = album_id
        self.extended = extended
        self.count = count

    def save_photo_in_YanDisk(self, token_yadisk):
        self.token_yadisk = token_yadisk
        params = {
            "access_token": self.access_token,
            "v": self.v,
            "owner_id": self.owner_id,
            "album_id": self.album_id,
            "extended": self.extended,
            "count": self.count
        }
        response = requests.get(url=self.url, params=params)
        foto_info = []
        json_faile = []
        # Вытаскиваем информацию о фото, добавляем с наибольшим разрешением
        for foto in response.json()["response"]["items"]:
            max_resolution = []
            for num, size in tqdm(enumerate(foto["sizes"]), desc='Поиск лучших фотографий'):
                # Условие для старых фоток, где значения = 0 и для первого разрешения. Добавим УРЛ и ТИП (для дальнейшего сравнения)
                if (size["height"] == 0 or size["width"] == 0) and num == 0:
                    max_resolution.append(size["type"])
                    max_resolution.append(size['url'])
                # Условие для старых фоток, где значения = 0. Сравниваем, согласно документации разрешение ('type') привязано к алфавиту
                elif (size["height"] == 0 or size["width"] == 0) and num > 0:
                    if size["type"] > max_resolution[0]:
                        max_resolution.clear()
                        max_resolution.append(size["type"])
                        max_resolution.append(size['url'])
                #  Условие для первого разрешения, перемножаем высоту и ширину получаем число (пиксели). Добавим УРЛ и ЧИСЛО (пиксели)
                elif (size["height"] != 0 or size["width"] != 0) and num == 0:
                    max_resolution.append(size["type"])
                    max_resolution.append(size["url"])
                    max_resolution.append(int(size["height"]) * int(size["width"]))
                # Условие для дальнейших разрешений. Сравниваем по пикселям
                elif (size["height"] != 0 or size["width"] != 0) and num > 0:
                    if int(size["height"]) * int(size["width"]) > max_resolution[2]:
                        max_resolution.clear()
                        max_resolution.append(size["type"])
                        max_resolution.append(size["url"])
                        max_resolution.append(int(size["height"]) * int(size["width"]))

            # Добавим в список информацию о самом лучшем фото (УРЛ и кол-во Лайков)
            foto_info.append([max_resolution[1],foto["likes"]["count"]])
            json_faile.append({"file_name": f"{foto['likes']['count']}.jpg", "size": f"{max_resolution[0]}"})

            # Проверим есть ли фотографии с одинаковым кол-ом Лайков
            for h in tqdm(foto_info, desc='Проверка чтобы не было одинаковых лайков'):
                for n, _ in enumerate(foto_info):
                    # Условие для пропуска проверки между одинаковыми объектами
                    if h == foto_info[n]:
                        continue
                    # Условие сравнения Лайков. Если одинаковое количество, то добавим к Лайкам Дату
                    elif h[1] == foto_info[n][1]:
                        h[1] = h[1] + foto["date"]

        # Создадим новую папку (Вконтакте) на ЯД
        url_new_direct = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"OAuth {self.token_yadisk}"
        }
        params = {
            "path": "Вконтакте"
        }
        requests.put(url=url_new_direct, headers=headers, params=params)

        # Отправляем фотки в ново-созданную папку (Вконтакте) на ЯД, имя по лайкам и по дате (если повторяются лайки)
        for i in tqdm(foto_info, desc='Отправляем на ЯД'):
            yandex_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            image_url = i[0]
            page_response = requests.get(image_url)
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"OAuth {self.token_yadisk}"
            }
            params = {
                "path": f"/Вконтакте/{i[1]}"
            }
            response = requests.get(url=yandex_url, headers=headers, params=params)
            href = response.json()["href"]
            requests.put(url=href, data=page_response)

        with open("save_photo_in_YanDisk.json", "w") as f:
            json.dump(json_faile, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    access_token = ""
    token = ""
    x = VkPhotos(access_token, owner_id=1).save_photo_in_YanDisk(token_yadisk=token)