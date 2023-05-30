FROM python:alpine

WORKDIR /app

RUN apk --no-cache add git

RUN git clone https://github.com/jzl1/ip_scan .

RUN pip install -r requirements.txt

ENV TOKEN=<your_token>
ENV ALLOWED_CHAT_IDS=<comma_separated_chat_ids>
ENV CHAT_ID=<default_chat_id>
ENV API_KEY=<your_api_key>
ENV HOST=<your_host>

CMD ["python", "/app/bot.py"]
