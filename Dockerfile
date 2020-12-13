FROM python:3.8-slim

WORKDIR /app/

COPY . /app
COPY requirements.txt /app/

# Дополнительно клонировать репозиторий в корень проекта git+ssh://git@gitlab.com/playgendary-dev/it-automation/playgendary-services-python.git
EXPOSE 80

RUN pip3 install --upgrade pip
RUN pip3 install -r /app/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]