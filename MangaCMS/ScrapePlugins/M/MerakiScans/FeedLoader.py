

import bs4
import re

import urllib.parse
import time
import calendar
import dateutil.parser
import runStatus
import settings
import datetime

import MangaCMS.ScrapePlugins.LoaderBase
import nameTools as nt

# Only downlad items in language specified.
# Set to None to disable filtering (e.g. fetch ALL THE FILES).
DOWNLOAD_ONLY_LANGUAGE = "English"

class FeedLoader(MangaCMS.ScrapePlugins.LoaderBase.LoaderBase):



	logger_path = "Main.Manga.Meraki.Fl"
	plugin_name = "MerakiScans Link Retreiver"
	plugin_key = "meraki"
	is_manga     = True

	urlBase = "http://merakiscans.com/"
	feedUrl = "http://merakiscans.com/manga-list/"


	def extractItemInfo(self, soup):

		ret = {}
		container = soup.find("div", class_="mng_ifo")
		infoDiv = container.find("div", class_="col-md-8")

		titleDiv = soup.find("h1", class_='ttl')
		ret["title"] = titleDiv.get_text()

		items = infoDiv.find_all("p")

		ret["note"] = " ".join(items[0].strings)   # Messy hack to replace <br> tags with a ' ', rather then just removing them.

		# And clean out the non-breaking spaces
		ret["note"] = ret["note"].replace(chr(0xa0), ' ')

		for item in items:
			text = item.get_text().strip()
			if not ":" in text:
				continue

			what, text = text.split(":", 1)
			if what == "Category":
				tags = [tag_link.get_text() for tag_link in item.find_all("a")]

				ret["tags"] = [tag.lower().strip().replace(" ", "-") for tag in tags]


		return ret

	def getItemPages(self, url):
		page = self.wg.getpage(url)

		soup = bs4.BeautifulSoup(page, "lxml")
		baseInfo = self.extractItemInfo(soup)

		ret = []
		for link in soup.find_all("a", class_="lst"):
			item = {}

			url = link["href"]
			chapTitle = link.find("b", class_="val")
			chapTitle = chapTitle.get_text()

			chapDate = link.find("b", class_="dte")

			date = dateutil.parser.parse(chapDate.get_text(), fuzzy=True)

			item["origin_name"]         = "{series} - {file}".format(series=baseInfo["title"], file=chapTitle)
			item["source_id"]           = url
			item["series_name"]         = baseInfo["title"]
			item["tags"]                = baseInfo["tags"]
			item["additional_metadata"] = {'note' : baseInfo["note"]}
			item["posted_at"]           = date

			ret.append(item)

		return ret


	def getSeriesUrls(self):
		ret = []
		print("wat?")
		page = self.wg.getpage(self.feedUrl)
		soup = bs4.BeautifulSoup(page, "lxml")
		divs = soup.find_all("div", class_="img_wrp")
		for div in divs:
			url = div.a["href"]
			ret.append(url)

		return ret

	def get_feed(self):
		# for item in items:
		# 	self.log.info( item)
		#

		self.log.info( "Loading MerakiScans Items")

		ret = []

		seriesPages = self.getSeriesUrls()


		for item in seriesPages:

			itemList = self.getItemPages(item)
			for item in itemList:
				ret.append(item)

			if not runStatus.run:
				self.log.info( "Breaking due to exit flag being set")
				break
		self.log.info("Found %s total items", len(ret))
		return ret





if __name__ == "__main__":
	import utilities.testBase as tb

	with tb.testSetup(load=False):

		run = FeedLoader()
		run.do_fetch_feeds()
		# run.getFeed()


