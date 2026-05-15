#!/bin/bash

# Переходим в директорию проекта (измените на название вашего репозитория)
cd multimodal_agent

export PORT=5000
unset PIP_USER

# Создаем виртуальное окружение если не существует
if [ ! -d "venv" ]; then
    echo "Creating virtual environment with system site packages..."
    python3 -m venv venv --system-site-packages
fi

# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем зависимости
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt || echo "Pip install failed, but continuing..."
fi

echo "Starting application..."
python main.py