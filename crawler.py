import logging
import os
import lxml.html
import re
from urllib.parse import urlparse
from corpus import Corpus

from collections import defaultdict

logger = logging.getLogger(__name__)

class Crawler:
    """
    This class is responsible for scraping urls from the next available link in frontier and adding the scraped links to
    the frontier
    """

    def __init__(self, frontier):
        self.frontier = frontier
        self.corpus = Corpus()
        
        #create variables needed for analtics calculation 
        self.traps = set()
        self.downloads = set()
        self.valid_links_count = 0
        self.url_with_most_valid_links = ''
        self.current_highest_valid_link_count = -1
        self.subdomains_and_frequencies = defaultdict(int)

    def start_crawling(self):
        """
        This method starts the crawling process which is scraping urls from the next available link in frontier and adding
        the scraped links to the frontier
        """
        while self.frontier.has_next_url():
            self.valid_links_count = 0
            url = self.frontier.get_next_url()
            logger.info("Fetching URL %s ... Fetched: %s, Queue size: %s", url, self.frontier.fetched, len(self.frontier))
            url_data = self.fetch_url(url)
            self.subdomains_and_frequencies['.'.join(urlparse(url).netloc.split('.')[:-2]).lstrip("www.")] += 1
            
            for next_link in self.extract_next_links(url_data):
                if self.corpus.get_file_name(next_link) is not None:
                    if self.is_valid(next_link):
                        self.valid_links_count += 1
                        self.frontier.add_url(next_link)
                        self.downloads.add(next_link)
                        file_path = self.corpus.get_file_name(next_link)
                        file_list = file_path.split('/')
                        doc_ID = str(file_list[2] + file_list[3])
                        posting_list = read_file(next_link, doc_ID)
                        tf_score(posting_list)
                        
                        
                        
            if self.valid_links_count > self.current_highest_valid_link_count:
                self.current_highest_valid_link_count = self.valid_links_count
                self.url_with_most_valid_links = url
        self.printAnalytics()
                
    def fetch_url(self, url):
        """
        This method, using the given url, should find the corresponding file in the corpus and return a dictionary
        containing the url, content of the file in binary format and the content size in bytes
        :param url: the url to be fetched
        :return: a dictionary containing the url, content and the size of the content. If the url does not
        exist in the corpus, a dictionary with content set to None and size set to 0 can be returned.
        """
        #get the file name using the method defined in corpus 
        file_name = self.corpus.get_file_name(url)
        if file_name is None:   #if file is none, return the empty dictionary with content set to None and size set to 0
            url_data = {
                "url": url,
                "content": None,
                "size": 0
            }
        else:                   #if file returns a valid file name 
            f1 = open(file_name, 'rb')      #open that file (binary format for reading)
            content = ""
            for line in f1:
                content = content + str(line)       #go through each line and add it to a content string 
            file_info = os.stat(file_name)          #for the sake of converting to right size 
            size = file_info.st_size                
            url_data = {
                "url": url,
                "content": content,
                "size": size
            }
        
        return url_data

    def extract_next_links(self, url_data):
        """
        The url_data coming from the fetch_url method will be given as a parameter to this method. url_data contains the
        fetched url, the url content in binary format, and the size of the content in bytes. This method should return a
        list of urls in their absolute form (some links in the content are relative and needs to be converted to the
        absolute form). Validation of links is done later via is_valid method. It is not required to remove duplicates
        that have already been fetched. The frontier takes care of that.

        Suggested library: lxml
        """
        #get the content from the dictionary, convert it to an html document, make the links absolute
        #iterlinks() will return all the links but only the 3rd element (index 2) will have the actual url so lets take that from every link
        #and add it to a list called outputLinks
        
        content = url_data["content"]
        html_doc = lxml.html.document_fromstring(content)
        html_doc.make_links_absolute(url_data["url"])
        outputLinks = [i[2] for i in html_doc.iterlinks()]
        
        #outputLinks = []
        return outputLinks

    def is_valid(self, url):
        """
        Function returns True or False based on whether the url has to be fetched or not. This is a great place to
        filter out crawler traps. Duplicated urls will be taken care of by frontier. You don't need to check for duplication
        in this method
        """
        #if a url is too long, good chance its a trap. lets check the link and set a threshold of 150
        if len(url) > 150:
            self.traps.add(url)
            return False
        
        #if we have a path like subsets/subsets or subsets/somethingelse/subsets etc. then it's a duplicate and my group decided it's a trap
        url_components = urlparse(url).path.strip('/').split("/") 
        setUrl = set(url_components)
        if len(url_components) != len(setUrl):
            self.traps.add(url)
            return False
        
        #bad queries (queries that have too many '&' are most likley traps) so we'll set a threshold of 2 for what count as a bad query 
        parameters = url.split('?')
        if len(parameters) > 1:
            if parameters[1].count('&') >= 2:
                self.traps.add(url)
                return False
        
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        try:
            return ".ics.uci.edu" in parsed.hostname \
                   and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4" \
                                    + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
                                    + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
                                    + "|thmx|mso|arff|rtf|jar|csv" \
                                    + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower())

        except TypeError:
            print("TypeError for ", parsed)
            return False
        return True

    def printAnalytics(self):
        file = open("analytics.txt", "w")
        #part 1 of analytics
        file.write("Subdomains visited and their frequency:\n")
        for key, value in sorted(self.subdomains_and_frequencies.items(), key=lambda x: (-x[1], x[0])):
            file.write(key+":"+str(value)+'\n')
        
        #part 2 of analytics 
        file.write("Page with the most valid outlinks:\n")
        file.write(self.url_with_most_valid_links +'\n')
        
        #part 3 of analytics 
        file.write("List of downloaded urls:\n")
        for elem in self.downloads:
            file.write(elem + '\n')
        file.write("List of traps:\n")
        for elem in self.traps:
            file.write(elem+'\n')
        
        file.close()
        