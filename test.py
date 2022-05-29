from DataCollection import ImageScraper


img_scrapper = ImageScraper(browser_name='CHROME', path='PATH TO YOUR BROWSER\'S WEBDRIVER')
collection = img_scrapper.extract_all_img_links_related_to_words(['Valley', 'plain', 'petal'])
for k in collection:
    collection[k] = collection[k][:1] # Download 1 image from each word
img_scrapper.download_all_img_scrapper(collection, 'D:\\test', 'Your user-agent')