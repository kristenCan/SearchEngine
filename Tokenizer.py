from collections import defaultdict
from collections import deque
from bs4 import BeautifulSoup
from nltk.stem import WordNetLemmatizer
import Doc
import lxml.html

class Tokenizer:
    
    lemmatizer = WordNetLemmatizer() 
    
    def read_file(url, doc_ID, index):
        doc = Doc()
        doc.doc_ID = doc_ID
        file = open(url, 'r')
        content = list()
        page = BeautifulSoup(file.content, 'xml')
        content.append(page.find_all('p')[0].get_text())
        content.append(page.find_all('meta', name= 'keywords')[0].get_text())
        content.append(page.find_all('title')[0].get_text())
        tokenizer(content, doc, index)
        
    def tokenizer(content, doc, index):
        for elem in content:
            wordcount = 0
            words = re.findall(r'[a-zA-Z0-9]+', elem) 
            tokens = defaultdict()
            for word in words:
                wordcount += 1
                tokens[word] += 1
            for key in tokens:
                tupKey = (key, 0)
                doc.frequency = tokens[key]
                doc.tf_score = tf_score(doc.frequency, wordcount)
                if key not in index:
                    if elem == content[0]:
                        doc.multiplier = 1.0
                    elif elem == content[1]:
                        doc.multiplier = 1.3
                    elif elem == content[2]:
                        doc.multiplier = 1.5
                else:
                    if elem == content[0]:
                        doc.multiplier *= 1.0
                    elif elem == content[1]:
                        doc.multiplier *= 1.3
                    elif elem == content[2]:
                        doc.multiplier *= 1.5
                        
                index[tupKey].append(doc)
                        
        
    def tf_score(frequency, wordcount):
        return frequency/wordcount
    
        
        
        