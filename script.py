import requests
import pandas as pd
import smtplib
import random
import re
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from time import sleep

# Load environment variables from .env file
load_dotenv()

# Don't forget to add {page} to page=
def main():
    base_url = 'https://www.example.com/x/blah/{page}/blah' #enter url here, if scraping multiple pages use {page} where page# is in url
    password = os.getenv('PASSWORD')
  
    
    
    def random_user_agent(): 
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62",    
        ]
        return random.choice(user_agents)


        
    def fetch_listings(url):
        headers = {
        "User-Agent": random_user_agent(),
        "Referer": "https://www.google.com",
        }
        response = requests.get(url, headers=headers)
        sleep(random.uniform(1,5))
        soup = BeautifulSoup(response.content, "html.parser")
        return soup
# Find HTML elements (In this example was for real estate listings)
    def extract_data(soup):
        listings = soup.find_all("div", class_="item-cnt")
        title = [listing.find('div', {'class': 'address-container'}).text.strip() for listing in listings]
        link = ["https://www.example.com" + listing.find('a', rel='noopener')['href'] for listing in listings]
        location = [re.search(r'[^,]*,\s*([^,]*),\s*[^,]*$', listing.find('div', {'class': 'address-container'})['data-address']).group(1) for listing in listings]
        price = [listing.find('span', {'class': 'green'}).text.strip() for listing in listings]
        property_type = [listing.find('li', {'class': 'property-type'}).text.strip() for listing in listings]
        lot_size = [listing.find('li', {'data-label': 'Lot Size'}).find('strong').text.strip() if listing.find('li', {'data-label': 'Lot Size'}) else 'N/A' for listing in listings]
        sqft = [listing.find('li', {'data-label': 'Sqft'}).find('strong').text.strip() if listing.find('li', {'data-label': 'Sqft'}) else 'N/A' for listing in listings]
        baths = [listing.find('li', {'data-label': 'Baths'}).find('strong').text.strip() if listing.find('li', {'data-label': 'Baths'}) else 'N/A' for listing in listings]
        beds = [listing.find('li', {'data-label': 'Beds'}).find('strong').text.strip() if listing.find('li', {'data-label': 'Beds'}) else 'N/A' for listing in listings]
        
        real_estate = pd.DataFrame({'Title': title, 'Location': location, 'Price': price, 'Property Type': property_type, 'Lot Size': lot_size, 'Sqft': sqft, 'Baths': baths, 'Beds': beds, 'Link': link})

        print(real_estate)
        return real_estate

    def get_last_page(soup):
        return 2 # define how many pages you'll search here
    
    def send_email(sender, recipient, file_name, subject, content, smtp_server, smtp_port, password):
        
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(content, "plain"))

        with open(file_name, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {file_name}")
            msg.attach(part)

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())
        server.quit()

    file_name = "scrape_results.csv"

    # Fetch and extract the data
    page = 1
    soup = fetch_listings(base_url.format(page=1))
    last_page = get_last_page(soup)
    all_real_estate = pd.DataFrame(columns=['Title', 'Price', 'Property Type'])
    num_pages = 40 # define how many pages you'll search here
    for page in range(1, num_pages + 1):
        url = base_url.format(page=page)
        soup = fetch_listings(url)
        real_estate = extract_data(soup)

        if real_estate.empty:
            break

        all_real_estate = pd.concat([all_real_estate, real_estate], ignore_index=True)
    # Save the data to a CSV file
    all_real_estate.to_csv(file_name, index=False)
    
    # Send the email
    sender = "send_address@email.com"
    recipient = "recipient_address@email.com"
    subject = "Test"
    content = "testing"
    smtp_server = "smtp.gmail.com" # Find server and port for your email server
    smtp_port = "587"

    send_email(
        sender,
        recipient,
        file_name,
        subject,
        content,
        smtp_server,
        smtp_port,
        password,
    )

if __name__ == "__main__":
    main()


