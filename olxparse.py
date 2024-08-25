from bs4 import BeautifulSoup
import requests

class Car(object):
	title = ''
	year = ''
	engine = ''
	power = ''
	colour = ''
	odometer = ''
	price = ''
	fuel = ''
	URL = ''
	image = ''

def ParseOLX(listingURL):
	if "otomoto" in listingURL:
		listing = ParseOtomoto(listingURL)
		return listing
	else:
		listingPage = requests.get(listingURL)
		listingSoup = BeautifulSoup(listingPage.content, "html.parser")
		listing = Car()
		listing.URL = listingURL

		titlecontainer = listingSoup.find(attrs={"data-testid":"ad_title"})
		if titlecontainer and titlecontainer.h4:
			listing.title = titlecontainer.h4.contents[0]
		pricecontainer = listingSoup.find(attrs={"data-testid":"ad-price-container"})
		if pricecontainer and pricecontainer.h3:
			listing.price = pricecontainer.h3.contents[0]
		img = listingSoup.find(attrs={"data-testid":"swiper-image"})['src']
		a = img.find(";s=")
		listing.image = img[:a]+";s=300x200"
		specs = listingSoup.find_all("ul")[1].find_all("li")
		for j in specs:
			text = str(j.p.contents[0])
			if text.startswith("Rok"):
				listing.year = text[15:]
			elif text.startswith("Przebieg"):
				listing.odometer = text[10:]
			elif text.startswith("Paliwo"):
				listing.fuel = text[8:]
			elif text.startswith("Kolor"):
				listing.colour = text[7:]
			elif text.startswith("Poj"):
				listing.engine = text[14:]
			elif text.startswith("Skrzynia"):
				listing.gearbox = text[17:]
			elif text.startswith("Moc"):
				listing.power = text[13:]

		return listing

def ParseOtomoto(listingURL):
	listingPage = requests.get(str(listingURL))
	listingSoup = BeautifulSoup(listingPage.content, "html.parser")
	listing = Car()
	listing.URL = listingURL

	titlecontainer = listingSoup.find(class_="offer-title")
	if titlecontainer:
		listing.title = titlecontainer.contents[0]
	listing.price = str(listingSoup.find(class_="offer-price__number").contents[0])+str(listingSoup.find(class_="offer-price__currency").contents[0])
	details = listingSoup.find(attrs={"data-testid":"main-details-section"}).find_all(attrs={"data-testid":"detail"})
	img = listingSoup.find(attrs={"data-testid":"photo-gallery-item"}).img['src']
	a = img.find(";s=")
	listing.image = img[:a]+";s=300x200;q=80"
	
	for i in details:
		label = str(i['aria-label'])
		if label.startswith("Pojemno"):
			listing.engine = label[18:]
		elif label.startswith("Moc"):
			listing.power = label[4:]
		elif label.startswith("Przebieg"):
			listing.odometer = label[9:]
		elif label.startswith("Skrzynia"):
			listing.gearbox = label[16:]
		elif label.startswith("Rodzaj"):
			listing.fuel = label[14:]
		
	det = listingSoup.find_all(attrs={"data-testid":"advert-details-item"})
	for i in det:
		con = i.find_all("p")
		if con[0].contents[0].startswith("Rok"):
			if len(con) > 1:
				listing.year = con[1].contents[0]
		elif con[0].contents[0].startswith("Kolor"):
			listing.colour = con[0].parent.a.contents[0]
	
	return listing

def SearchOtomoto(soup, max):
	try:
		container = soup.find(attrs={"data-testid":"search-results"})
		listings = container.find_all("article")
		listingURLs = []
		k = 0
		for i in range(0, len(listings), 2): #Otomoto has an "article" tag inside "article" tag that is a listing itself
		    if k >= max:
		        break
		    k = k + 1
		    url = listings[i].find("a")['href']
		    listingURLs.append(url)
		return listingURLs
	except Exception as Ex:
		return Ex

def SearchOLX(soup, max):
	try:
		listings = soup.find_all(attrs={"data-testid": "l-card"})
		listingURLs = []
		k = 0
		for i in listings:
			if k >= max:
				break
			k = k + 1
			url = i.find("a")['href']
			if url.startswith("/d/"):
				url = "https://olx.pl"+url
				listingURLs.append(url)
			else:
				listingURLs.append(url)
		return listingURLs
	except Exception as Ex:
		return Ex

def search(URL, maxnum=5):
	if "otomoto" in URL or "olx.pl" in URL:
		page = requests.get(URL)
		soup = BeautifulSoup(page.content, "html.parser")
		listingsparsed = []
		if URL.find("otomoto") != -1:
			print("what")
			SearchOtomoto(soup, maxnum)
			listings = SearchOtomoto(soup, maxnum)
			for i in range(0, len(listings)):
				listingsparsed.append(ParseOtomoto(i))
		else:
			listings = SearchOLX(soup, maxnum)
			for i in listings:
				j = ParseOLX(i)
				listingsparsed.append(ParseOLX(i))
		return listingsparsed
	else:
		return("This is not OLX.pl or OtoMoto.pl link.")

def parse(URL):
	if "otomoto" in URL:
		return ParseOtomoto(URL)
	elif "olx.pl" in URL:
		return ParseOLX(URL)
	else:
		return("this doesn't seem to be an OLX.pl or OtoMoto.pl link")

