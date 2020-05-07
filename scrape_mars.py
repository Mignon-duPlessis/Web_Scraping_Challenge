# import dependencies
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import requests
import time

# create function


def scrape_all():

    # set up path to browser
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)
    news_title, news_p = nasa_mars_news(browser)

# set up dictionary for scraping
    data = {
        "page_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_image(browser),
        "hemispheres_urls": hemispheres_urls(browser),
        "mars_weather": twitter_weather(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }

# quit browser and return dictionary
    browser.quit()
    return data


def nasa_mars_news(browser):
    url = "https://mars.nasa.gov/news/"

    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    
    news_title = soup.find('div', class_="content_title").find('a').text
    news_p = soup.find('div', 'rollover_description_inner').text

    return news_title, news_p


def featured_image(browser):
    url2 = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url2)

    # move through pages on site
    time.sleep(5)
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(5)
    browser.click_link_by_partial_text('more info')
    time.sleep(5)

    # pull html text
    response = browser.html

    soup = BeautifulSoup(response, 'html.parser')

    image_link = soup.find('figure', 'lede').a['href']
    site_link = 'https://www.jpl.nasa.gov'
    featured_image_url = site_link + image_link

    return featured_image_url


def hemispheres_urls(browser):

    url5 = ("https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars")
    browser.visit(url5)
    response = browser.html
    soup = BeautifulSoup(response, 'html.parser')

    returns = soup.find('div', 'collapsible results')


    # retrieve all anchors in each class pulled above
    hemispheres = returns.find_all('div', {"class": 'description'})

        # create empty list to hold dictionaries
    hemisphere_image_urls = []

    # loop through all anchors for each hemisphere class
    for description in hemispheres:
        a = description.find('a')

        # retrieve title and link to specific hemisphere page
        title = a.h3.text
        link = 'https://astrogeology.usgs.gov' + a['href']

        # visit above link
        browser.visit(link)
        time.sleep(5)

        # retrieve link to image
        page = browser.html
        results = BeautifulSoup(page, 'html.parser')
        image_link = results.find('div', 'downloads').find('li').a['href']

        # create empty dictionary for title & image
        image_dict = {}
        image_dict['title'] = title
        image_dict['img_url'] = image_link

        # add image_dict to empty list from above
        hemisphere_image_urls.append(image_dict)

    return hemisphere_image_urls


def twitter_weather(browser):
    url3 = 'https://twitter.com/marswxreport?lang=en'
    response = requests.get(url3)

    soup = BeautifulSoup(response.text, 'html.parser')

    # The latest Mars weather tweet from the page
    results = soup.find_all('div', class_='js-tweet-text-container')
    # Look for entries that display weather related words to exclude non weather related tweets
    for result in results:
        mars_weather = result.find('p').text
        if 'Sol' and 'pressure' in mars_weather:
            print(mars_weather)
            break
        else:
            pass

    return mars_weather


def mars_facts():

    url4 = 'https://space-facts.com/mars/'

    fact_tables = pd.read_html(url4)

    df = fact_tables[0]
    df.columns = ['MARS PROFILE', 'Information']
    html_table = df.to_html()

    return html_table


if __name__ == "__main__":

    print(scrape_all())
