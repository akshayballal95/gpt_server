import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

urls = []

def scrape_website(url):
    # Send a GET request to the website
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Create a BeautifulSoup object with the website's HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all anchor tags on the page
        anchor_tags = soup.find_all('a')

        urls.append(url)
        
        # Iterate over each anchor tag
        for tag in anchor_tags:
            # Get the href attribute of the anchor tag
            href = tag.get('href')
            
            # Join the URL of the href with the base URL of the website
            absolute_url = urljoin(url, href)
            
            # Print the absolute URL
            urls.append(absolute_url)
            
    else:
        # Print an error message if the request was unsuccessful
        print(f"Failed to scrape {url}. Error: {response.status_code}")

# Enter the URL of the website you want to scrape
website_url = 'https://akshaymakes.com/blogs'
my_urls = ['https://akshaymakes.com/blogs', 'https://akshaymakes.com', 'https://akshaymakes.com/resume', 'https://akshaymakes.com/projects']

for website_url in my_urls:
  scrape_website(website_url)

for url in urls:
  if "akshaymakes" in url and 'resume' not in url:
      response = requests.get(url)
      soup = BeautifulSoup(response.content, 'html.parser')
      text_content = soup.get_text()
      
      # Print the text content
      if not os.path.exists('files') : os.mkdir("files")

      file_name = url.split('/')[-1]
      with open('files/'+file_name+".txt", 'w', encoding='utf-8') as f:
        f.write(text_content)
