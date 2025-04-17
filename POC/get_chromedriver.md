## Install Chrome in linux

wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

sudo dpkg -i google-chrome-stable_current_amd64.deb

sudo apt-get install -f

google-chrome --version

## Insalling chromedriver 

check for latest version of chrome and get its driver here https://googlechromelabs.github.io/chrome-for-testing/

curl -O https://storage.googleapis.com/chrome-for-testing-public/132.0.6834.83/linux64/chromedriver-linux64.zip

unzip chromedriver-linux64.zip

sudo mv chromedriver-linux64/chromedriver /usr/bin/

sudo chmod +x /usr/bin/chromedriver

