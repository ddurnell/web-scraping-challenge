from splinter import Browser
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd

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
    return featured_image_url

def scrape_mars_weather(browser, url):
    browser.visit(url)
    # sending get request and saving the response as response object 
    r = requests.get(url = url) 
  
    # extracting the end result since the whole thing is javascript 
    html = r.text
    soup = bs(html)

    # gather the tweets
    tweets = soup.find_all("div", class_="js-tweet-text-container")

    # extract the .jpg file path
    for t in tweets:
        p = t.contents[1]
        text = p.contents[0]
        if text.startswith('InSight'):
            mars_weather = text
            break
    return mars_weather

def scrape_mars_facts(browser, url):
    # go to NASA and get the soup
    browser.visit(url)
    html = browser.html
    soup = bs(html, 'lxml')

    tables = pd.read_html(url)
    fact_table = tables[0]
    print(fact_table)

    return fact_table.to_html()

# Subfunction for scrape_mars_hemispheres
# For each url, navigate to the enhanced tif, and return its link
def get_enhanced_image(browser, url):
#     print(url)
    browser.visit(url)
    html = browser.html
    soup = bs(html, 'lxml')    
    ds = soup.find_all('div', class_='downloads')
    for d in ds:
        link = d.a
        h = link.get('href')
#         print(h)
    return h

def scrape_mars_hemispheres(browser, url):
    # go and get the soup
    browser.visit(url)
    html = browser.html
    soup = bs(html, 'lxml')

    # Extract the titles and the links
    result = soup.find("div", class_="collapsible results")

    next_dict = {} # the links to get to the enhanced images
    results = result.find_all('div')
    for r in results:
        item = r.contents[1]
        links = item.find_all('a')
        for link in links:
            title = link.find('h3').text
            href = link['href']
            href = "https://astrogeology.usgs.gov/" + href
            next_dict[title] = href

    # Go find the actual url for the enhanced image
    # Loop through the dictionary
    results_list = []
    for key in next_dict:
    #     print(key)
    #     print(next_dict[key])
        url = get_enhanced_image(browser, next_dict[key])
        d = {"title": key, "img_url": url}
        results_list.append(d)
    return results_list


def scrape():
    browser = init_browser()
    mars_data = {}

    # get mars news
    mars_news = scrape_mars_news(browser, 'https://mars.nasa.gov/news/')
    mars_data['news'] = mars_news

    # get mars image
    mars_image = scrape_mars_image(browser, 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars')
    mars_data['image'] = mars_image
    
    # get mars image
    mars_weather = scrape_mars_weather(browser, 'https://twitter.com/marswxreport?lang=en')
    mars_data['weather'] = mars_weather

    # get mars facts table
    mars_facts = scrape_mars_facts(browser, 'https://space-facts.com/mars/')
    mars_data['facts'] = mars_facts

    # get mars hemispheres links
    mars_hems = scrape_mars_hemispheres(browser, 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars')
    mars_data['hemisphere_image_urls'] = mars_hems

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data

if __name__ == "__main__":
    mars_dict = scrape()
    print(mars_dict)
