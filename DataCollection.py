from selenium import webdriver
import concurrent.futures, requests, json, time, os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ImageScraper():
    '''
    __init__ - 
        browser_name - pass any of chrome, edge, firefox
        path - path to the drivers of the browser
    
    extract_all_img_links_related_to_words -
        words - list of all topics on collect images on.
    
    download_all_img - 
        collection - dictionary with all words as keys and values as links of images. Could be obtained using extract_all_img_links_related_to_words method.
        path - path of directory where images will be stored.
    '''
    def __init__(self, path, browser_name='CHROME'):
        d = {
            'CHROME': webdriver.Chrome,
            'EDGE': webdriver.Edge,
            'FIREFOX': webdriver.Firefox
        }

        assert browser_name in d.keys(), 'only CHROME, EDGE and FIREFOX can be used as browser names'
        self.DRIVER = d[browser_name]
        self.PATH = path

    def __fetch_links(self, word, wait_time):
        
        # Opens browser and searches for given link
        driver = self.DRIVER(executable_path=self.PATH)
        driver.get("https://www.bing.com/images/search?q=" + word + "&qft=+filterui%3aimagesize-custom_1920_1080+filterui%3aphoto-photo+filterui%3alicense-L1&form=IRFLTR&first=1&tsc=ImageBasicHover")

        prev_height=0
        # Loading whole page
        while True:
            time.sleep(wait_time)
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);') # scroll down the page
            new_height = driver.execute_script("return document.body.scrollHeight;") # returns height

            # Check if previous height and new height
            # after scrolling down the page is same 
            # or not
            if prev_height==new_height:
                btn = driver.find_elements_by_link_text('See more images')
                if len(btn)==0: # if button for more images to load does not exist then break the loop 
                    break
                
                # Wait until button is clickable
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable(btn[0]))
                # Click the button
                driver.execute_script("arguments[0].click();", btn[0])

            prev_height = new_height
            
        anchor_tags, links = driver.find_elements_by_class_name('iusc'), []

        # Some preprocessing for image urls
        for a in anchor_tags: 
            index = a.get_attribute('m').find('"murl":"')
            link = a.get_attribute('m')[index + len('"murl":"'):].split('"')[0]
            jpg, jpeg = link.find('jpg'), link.find('jpeg')
            if jpg>0 and jpeg>0:
                if jpg < jpeg:
                    link = link[:jpg + len('jpg')]
                else:
                    link = link[:jpeg + len('jpeg')]
            else:
                if jpg<0:
                    link = link[:jpeg + len('jpeg')]
                else:
                    link = link[:jpg + len('jpg')]
            links.append(link)
        
        # Close the window
        driver.close()
                
        return [word, links]


    def extract_all_img_links_related_to_words(self, words, wait_time=2):
        '''
            words: List of words to extract urls for.
            wait_time: Time to wait after page is scrolled down 
        '''
        # Stores image urls related to each word
        collection = dict()
        for word in words:
            print(word)
            ele = self.__fetch_links(word, wait_time)
            collection[ele[0]] = ele[1]

        return collection

    def download_all_imgs(self, collection, path, user_agent):
        def download_helper(word, link, path):

            headers = {'User-Agent':user_agent}
            image = requests.get(link, headers=headers, stream=True).content
            image_name = link.split('/')[-1]

            # Check if directory exist or not 
            if not os.path.exists(f'{path}/{word}'):
                os.makedirs(f'{path}/{word}') 

            # Writing images
            with open(f'{path}/{word}/{image_name}', 'wb') as file: 
                file.write(image)

        for word, links in collection.items():
            # manages multi threading
            with concurrent.futures.ThreadPoolExecutor() as executor: 
                for link in links:
                    executor.submit(download_helper, word, link, path)

    
    def write_dictionary(self, dictionary, path):
        with open(path, 'w') as f:
            f.write(json.dumps(dictionary))

    def read_dictionary(self, path):
        with open(path) as f:
            json_data = json.load(f)
            return json_data
            