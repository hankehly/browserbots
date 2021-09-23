FROM python:3.9.7

LABEL org.opencontainers.image.source="https://github.com/hankehly/browserbots"

WORKDIR /app

# Install google-chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
RUN apt-get -y update && apt-get -y install google-chrome-stable libnss3

# Install chromedriver based on google-chrome version
RUN wget -q -O - https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$(google-chrome --version | cut -d' ' -f3 | cut -d. -f1-3) > LATEST_RELEASE
RUN wget -q -O ./chromedriver_linux64.zip https://chromedriver.storage.googleapis.com/$(cat LATEST_RELEASE)/chromedriver_linux64.zip
RUN unzip ./chromedriver_linux64.zip && mv ./chromedriver /usr/local/bin/chromedriver

# Install python packages
COPY ./requirements.prod.txt .
RUN pip install -r ./requirements.prod.txt

# Copy the rest of the source code into the image
COPY . /app
ENV PYTHONPATH /app
