FROM python:3.9-alpine
ENV TELEGRAM="${TELEGRAM}"
RUN mkdir /bot
ADD . /bot
WORKDIR /bot
RUN pip3 install requests python-crontab python-telegram-bot
CMD ["python3", "bot.py"]
