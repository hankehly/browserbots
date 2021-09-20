download_chromedriver_macos:
	@rm -f bin/chromedriver
	@mkdir -p bin
	@wget https://chromedriver.storage.googleapis.com/93.0.4577.63/chromedriver_mac64.zip
	@unzip chromedriver_mac64.zip
	@rm -f chromedriver_mac64.zip
	@mv chromedriver bin
