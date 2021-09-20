FROM python:3.9.7

WORKDIR /app

# Install google-chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
RUN apt-get -y update && apt-get -y install google-chrome-stable libnss3

# Install chromedriver based on google-chrome version
RUN wget -q -O - https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$(google-chrome --version | cut -d' ' -f3 | cut -d. -f1-3) > LATEST_RELEASE
RUN wget -q -O ./chromedriver_linux64.zip https://chromedriver.storage.googleapis.com/$(cat LATEST_RELEASE)/chromedriver_linux64.zip
RUN unzip ./chromedriver_linux64.zip && mv ./chromedriver /usr/local/bin/chromedriver

COPY . /app

# Install python packages
RUN pip install -r ./requirements.prod.txt

ENV PYTHONPATH /app

LABEL org.opencontainers.image.source="https://github.com/hankehly/browserbots"
