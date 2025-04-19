import requests
from bs4 import BeautifulSoup

# The disguised Discord Tenor URL
def save_gif(tenor_url):

    # Step 1: Follow the redirect to get the actual webpage
    response = requests.get(tenor_url, allow_redirects=True)
    webpage_url = response.url  # This is now the real Tenor page

    # Step 2: Fetch the webpage HTML
    webpage = requests.get(webpage_url)
    soup = BeautifulSoup(webpage.text, 'html.parser')

    # Step 3: Find the real GIF URL in meta tags
    gif_url = None
    for meta in soup.find_all('meta'):
        if meta.get('property') == 'og:image':
            gif_url = meta.get('content')
            break

    if gif_url:
        # Step 4: Download the actual GIF
        gif_data = requests.get(gif_url).content
        with open('gif.gif', 'wb') as f:
            f.write(gif_data)
        print("GIF downloaded successfully!")
    else:
        print("Could not find the direct GIF URL.")
