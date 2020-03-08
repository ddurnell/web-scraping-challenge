from splinter import Browser
from bs4 import BeautifulSoup as bs
import time


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "./chromedriver.exe"}
    browser = Browser("chrome", **executable_path, headless=True)
    return browser

def scrape_mars_news(browser, url):
    # go to NASA and get the soup
    browser.visit(url)
    html = browser.html
    soup = bs(html, 'lxml')

    # collect the latest News Title and Paragraph Text.
    # Assign the text to variables that you can reference later.
    news_list = soup.find_all("div", class_="image_and_description_container")
    news_dict = {}
    for news in news_list:
        result = []
        link = news.find("a")
        
        # extract the tag. The largest is the latest
        href = link.get('href')
        tag_list = href.split('/')
        tag = tag_list[2]
        
        # extract the title
        img = news.find_all('img', alt=True)
        title = img[1]['alt']
        result.append(title)
        
        # extract the description paragraph
        desc = news.find("div", class_="rollover_description_inner").get_text().strip()
        result.append(desc)
        news_dict[tag] = result

    # find the latest key
    big_key = max(k for k, v in news_dict.items())

    news_title = news_dict[big_key][0]
    news_p = news_dict[big_key][1]
    result = {'news_title':news_title, 'news_p':news_p}
    return result

def scrape_mars_image(browser, url):
    browser.visit(url)
    # go to full image
    browser.click_link_by_id('full_image')
    # click the more info button
    browser.click_link_by_partial_href('/spaceimages/details')
    html = browser.html
    soup = bs(html, 'lxml')
    # get the links to the full images
    full_images = soup.find_all("div", class_="download_tiff")

    # extract the .jpg file path
    for i in full_images:
        link = i.find("a")
        href = link.get('href')
        if href.endswith('.jpg'):
            path = href

    # make it a real, not relative path
    featured_image_url = "https:" + path
    result = {'mars_image':featured_image_url}
    return result

def scrape():
    browser = init_browser()
    mars_data = {}

    # get mars news
    mars_news = scrape_mars_news(browser, 'https://mars.nasa.gov/news/')
    mars_data['news'] = mars_news

    # get mars image
    mars_image = scrape_mars_image(browser, 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars')
    mars_data['image'] = mars_image
    
    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data

if __name__ == "__main__":
    mars_dict = scrape()
    print(mars_dict)
