FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Cria os dados de exemplo e sobe o painel
CMD ["sh", "-c", "python main.py init && python main.py sync && python main.py painel"]
