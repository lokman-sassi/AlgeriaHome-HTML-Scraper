from lxml import html
from bs4 import BeautifulSoup
import requests
import pymongo


all_listings_data = []


# Function to scrape listing details from a given link
def scrape_listing_details(url):
    try:
        response = requests.get(url)
        tree = html.fromstring(response.content)

        # Extracting title
        title = tree.xpath('//*[@id="item-content"]/h1/strong/text()')[0]
    

        # Extracting price
        price = tree.xpath('//*[@id="item-content"]/ul/li[1]/text()')[1]

        # Extracting location
        location = tree.xpath('//*[@id="item_location"]/li/text()')[0]

        # Extracting published date
        published_date = tree.xpath('//*[@id="item-content"]/ul/li[2]/text()')[1]
        date = published_date.replace(" Published date: ", "")

        # Extracting Description
        description_list = tree.xpath('//*[@id="description"]/p/text()')
        description = ''.join(description_list) 
        
        #Extracting category
        category = tree.xpath('//span[@itemprop="title"]/text()')

        #Extracting images (if found)
        image_urls = tree.xpath("//div[@class='thumbs-image']/a/@href")
        if not image_urls:
            image_urls = "No images were found"

        source = "Algeria Home"
        surface = None
    


        # Print the extracted information
        print("Title:", title)
        print("Price:", price)
        print("Location:", location)
        print("Description:", description)
        print("Images:", image_urls)
        print("Source:", source)
        print("Date:", date)
        print("Link:", url)
        print("Category:", category[1].strip())
        print("Surface", surface)
        print("-" * 50)

        listing_data = {
            "Title": title,
            "Price": price,
            "Location": location,
            "Description": description,
            "Images": image_urls,
            "Source": source,
            "Date": date,
            "Link": url,
            "Category": category[1].strip(),
            "Surface": surface
            }
        all_listings_data.append(listing_data)

    except Exception as e:
        print("Error while scraping data: ", str(e))
    

# Function to scrap all listings links
def scraping_listings_urls(page_url):
    try:
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the parent element of listings, then find all the individual listing items
        listings_parent = soup.find("ul", class_="listings_list")
        if listings_parent is None:
            print(f"No listings found on this page: {page_url}")
            return 
        
        listings = listings_parent.find_all("li", class_="listings_list listing-card")

        # Collect links of each listing
        for link in listings:
            listing_url = link.find("a", class_="listing-thumb")["href"]

            # Scraping details for each listing
            scrape_listing_details(listing_url)
        
    except Exception as e:
        print("Error while scrapinf listings urls: ", str(e))


# Function that stores the announcements in the data base
def save_to_database(records):
    client = pymongo.MongoClient('mongodb://localhost:27017')
    mydb = client["Real-Estate"]
    information = mydb.RealEstateListing
    if information is not None:
        existing_urls = []
        for record in information.find():
            existing_urls.append(record['Link'])
                
        for record in records:
            if record['Link'] in existing_urls:
                continue
            else:
                information.insert_one(record)
    
    else:
        information.insert_many(records)


# The main function to be executed
def main():

    listing_category = "maison-appartement-a-vendre"  # it can be: A vendre:["maison-appartement-a-vendre", "autres_1", "studio"] A louer["maison-appartement-a-louer", "chambres-a-louer-studio", "villa-a-louer"]
    base_url = f'https://www.algeriahome.com/{listing_category}'
    page = 1

    while True:
        page_url =f'{base_url}/{page}'
        response  = requests.get(page_url)
        tree = html.fromstring(response.content)
        endOfListingsMessage = tree.xpath('//*[@id="main"]/div/div[2]/div[2]/p/text()')
        
        try:  
            if endOfListingsMessage:
                break
            else:
                scraping_listings_urls(page_url)
                page+=1
        
        finally:
            save_to_database(all_listings_data)
            print("Scraped items: ", len(all_listings_data))
        
        
if __name__ == "__main__":
    main()

    

