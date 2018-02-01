from bs4 import BeautifulSoup
import requests
import csv
from pymongo import MongoClient
import datetime

class Scrapper(object):
	"""docstring for Scrapper"""
	def __init__(self, url = ''):
		self.url = url

		#connectio to database.
		try:
			client = MongoClient('localhost', 27017)
			self.db = client.pyTest
			date = datetime.datetime.now()
			self.db.status.insert({"connectedAt": date})
		except Exception as e:
			raise e
		

	def run(self):
		try:
			if(self.url == ''):
				raise ValueError('Url Missing.')

			self.getContent()
			self.filterContent()

		except Exception as e:
			raise e
		
	def getContent(self):
		print(self.url)
		try:
			data = requests.get(self.url)
			if(data.status_code != 200):
				raise ValueError('Error fetching data from: {}'.format(self.url))

			print("Data Loaded Successfully.")
			self.data = data
		except Exception as e:
			raise e
	
	def  filterContent(self):
		content = self.data.content
		soup = BeautifulSoup(content, 'html.parser')
		div = soup.find('div', 'table-responsive')
		
		#filter links
		self.links = div.find_all('a')

	def createList(self):
		self.uniLists = []

		for link in self.links:
			if(link.text == ''):
				continue

			self.uniLists.append({'name' : link.text, 'link': "https://www.4icu.org"+link['href']})
		

	def getUniDetails(self):
		i = 0
		documents = []
		for uni in self.uniLists:
			url = uni['link']
			uniContent = self.getUniContent(url)
			
			uSoup = BeautifulSoup(uniContent, 'html.parser')
			table = uSoup.find("table", "text-right")

			name        = uSoup.find('h1')
			description = uSoup.find_all('p')[1].text
			website 	= uSoup.findAll("a", {"itemprop" : "url"})[1].attrs['href']
			acronym		= uSoup.find("abbr").text	
			founded		= uSoup.find("span", {"itemprop": "foundingDate"}).text
			wRank       = table.findAll("td")[3].find("a").find("strong").text
			iRank       = table.findAll("td")[1].find("a").find("strong").text

			# print("Name {} | Indian Rank: {} | World Rank: {}".format(name.text, iRank, wRank))
			
			obj = {	
					"name": name.text, 
					"iRank": iRank, 
					"wRank": wRank, 
					"description": description,
					"website": website,
					"acronym": acronym,
					"founded": founded
				}

			self.writeToDB(obj)
			# documents.append(obj)		

			if(i == 30):
				break
			i = i + 1 

			# self.writeToDB(documents)	
			# print(documents)
	
	def getUniContent(self, url):
		print(url)
		try:
			data = requests.get(url)
			if(data.status_code != 200):
				# raise ValueError('Error fetching data from: {}'.format(url))
				return ''

			return data.content
		except Exception as e:
			return ''

			

	def writeToFile(self, filename = ''):
		if(filename == ''):
			filename = 'TestFile.csv'

		myFile = open(filename, 'w')  
		with myFile:  
			myFields = ['name', 'link']
			writer   = csv.DictWriter(myFile, fieldnames = myFields)			
			writer.writeheader()

			for link in self.links:
				if(link.text == ''):
					continue

				uniObj = {'name' : link.text, 'link': link['href']}

				self.uniLists.append(uniObj)
				writer.writerow(uniObj)
		
		print("File Written Successfully.")

	def writeToDB(self, object):
		self.db.universities.insert(object)
		print(object)
		print("Wrtten to DB successfully.")

	
if __name__ == '__main__':

	url = 'https://www.4icu.org/in/'
	sc  = Scrapper(url)

	sc.run()
	# sc.writeToFile()

	sc.createList()
	sc.getUniDetails()