import os
import re
import requests
from flask import Flask, request, render_template, jsonify

# --- Инициализация приложения Flask ---
app = Flask(__name__)

# --- Конфигурация API Pollinations ---
# Базовые URL для работы с API Pollinations. Ключи не требуются.
POLLINATIONS_TEXT_URL = "https://text.pollinations.ai/"
POLLINATIONS_IMAGE_URL = "https://image.pollinations.ai/prompt/"

# --- Функции для работы с ИИ ---

def generate_text(prompt: str) -> str:
    """
    Генерирует текст, отправляя POST-запрос к API Pollinations.
    """
    try:
        # Отправляем POST-запрос. Модель 'openai' — одна из лучших и стабильных.
        response = requests.post(
            POLLINATIONS_TEXT_URL,
            json={
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "model": "openai"  # Можно заменить на "mistral", "llama" и др.
            },
            timeout=60  # Ждём ответа до минуты
        )
        response.raise_for_status()  # Проверяем, не возникло ли ошибки HTTP
        return response.text  # API возвращает простой текст
    except requests.exceptions.RequestException as e:
        return f"❌ Ошибка при генерации текста: {str(e)}"

def generate_image(prompt: str) -> str:
    """
    Генерирует изображение, возвращая ссылку на него.
    Для этого просто формируется специальный URL.
    """
    encoded_prompt = requests.utils.quote(prompt)  # Кодируем промпт для URL
    # Параметры: ширина 1024, высота 1024, модель 'flux' (очень качественная)
    return f"{POLLINATIONS_IMAGE_URL}{encoded_prompt}?width=1024&height=1024&model=flux"

# --- Главный классификатор запросов ---
def classify_request(prompt: str) -> str:
    """
    Определяет, что нужно пользователю: текст или изображение.
    Ищет в промпте ключевые слова на русском и английском.
    """
    text_lower = prompt.lower()
    image_patterns = [
        r"нарисуй", r"нарисуйте", r"создай изображение", r"сгенерируй картинку",
        r"изобрази", r"draw", r"generate an image", r"create a picture",
        r"make an image", r"картинку", r"изображение"
    ]
    for pattern in image_patterns:
        if re.search(pattern, text_lower):
            return "image"
    return "text"

# --- Маршруты веб-приложения ---
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.get_json()
        prompt = data.get("prompt", "").strip()
        if not prompt:
            return jsonify({"error": "Промпт не может быть пустым"}), 400

        task_type = classify_request(prompt)
        if task_type == "text":
            result = generate_text(prompt)
            return jsonify({"type": "text", "content": result})
        else:
            image_url = generate_image(prompt)
            return jsonify({"type": "image", "content": image_url})

    # При GET-запросе просто показываем HTML-страницу
    return render_template("index.html")

# --- Точка входа для запуска ---
if __name__ == "__main__":
    # Привязываемся к 0.0.0.0, чтобы сервер был доступен извне
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)