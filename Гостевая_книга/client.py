import requests

BASE_URL = "http://127.0.0.1:5000"


def check(method, path, expected, **kwargs):
    response = requests.request(
        method, BASE_URL + path, timeout=5, **kwargs
    )
    status = "OK" if response.status_code == expected else "ERROR"

    print(f"\n{method} {path}")
    print(f"Status: {response.status_code} | Expected: {expected} | {status}")
    print("Response:", response.json())

    return response.json()


print("===== GUESTBOOK V2 + V3 TESTS =====")

# Создание заметок
note1 = check("POST", "/notes", 201,
              json={"author": "Ivan", "text": "Hello!"})
note2 = check("POST", "/notes", 201,
              json={"author": "Anna", "text": "Hi!"})
note3 = check("POST", "/notes", 201,
              json={"author": "Ivan", "text": "Second note"})

id1 = note1["id"]
id2 = note2["id"]
id3 = note3["id"]

# Ошибки создания
check("POST", "/notes", 400, json={"text": "No author"})
check("POST", "/notes", 400, json={"author": "", "text": "Empty author"})

# Получение заметок
check("GET", "/notes", 200)
check("GET", f"/notes/{id1}", 200)
check("GET", "/notes/999999", 404)

# Фильтрация и пагинация
check("GET", "/notes?author=Ivan", 200)
check("GET", "/notes?limit=2&offset=1", 200)
check("GET", "/notes?limit=abc", 400)
check("GET", "/notes?limit=101", 400)
check("GET", "/notes?offset=-1", 400)

# Полное обновление PUT
check("PUT", f"/notes/{id1}", 200,
      json={"author": "Ivan", "text": "Updated text"})
check("PUT", f"/notes/{id1}", 400,
      json={"text": "Missing author"})
check("PUT", "/notes/999999", 404,
      json={"author": "Test", "text": "Test"})

# Частичное обновление PATCH
check("PATCH", f"/notes/{id2}", 200,
      json={"text": "Changed with PATCH"})
check("PATCH", f"/notes/{id2}", 200,
      json={"author": "Maria"})
check("PATCH", f"/notes/{id2}", 400,
      json={"text": ""})
check("PATCH", "/notes/999999", 404,
      json={"text": "Test"})

# Лайки V3
check("POST", f"/notes/{id1}/like", 200)
check("POST", f"/notes/{id1}/like", 200)
check("POST", f"/notes/{id3}/like", 200)
check("POST", "/notes/999999/like", 404)

# Сортировка V3
check("GET", "/notes?sort=id&order=asc", 200)
check("GET", "/notes?sort=id&order=desc", 200)
check("GET", "/notes?sort=likes&order=desc", 200)
check("GET", "/notes?sort=likes&order=asc&limit=2", 200)
check("GET", "/notes?sort=wrong", 400)
check("GET", "/notes?order=wrong", 400)

# Статистика авторов
check("GET", "/authors", 200)

# Удаление одной заметки
check("DELETE", f"/notes/{id3}", 200)
check("DELETE", "/notes/999999", 404)

# Массовое удаление V3
check("DELETE", "/notes?author=Ivan", 200)
check("DELETE", "/notes?author=Unknown", 200)
check("DELETE", "/notes", 400)
check("DELETE", "/notes?author=", 400)

# Проверка оставшихся заметок
check("GET", "/notes", 200)
check("GET", "/authors", 200)

print("\n===== ALL TEST REQUESTS COMPLETED =====")
