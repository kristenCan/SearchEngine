from collections import deque
import Tokenizer
import math
import pickle

class Indexer:
    
    INVERTED_INDEX_DIR_NAME = "indexer_state"
    INVERTED_INDEX_FILE_NAME = os.path.join(".", INVERTED_INDEX_DIR_NAME, "inverted_index.pkl")
    
    def __init__(self, frontier):
        self.frontier = frontier
        self.index = defaultdict(deque())
        
    def create_inverted_index():
        num_files = 0
        while self.frontier.has_next_url():
            num_files += 1
            url = self.frontier.get_next_url()
            file_path = self.corpus.get_file_name(url)
            file_list = file_path.split('/')
            doc_ID = str(file_list[2] + file_list[3])
            read_file(url, doc_ID, self.index)
        
        for key in index:
            count_of_docs = self.index[key].count()
            key[1] = math.log10(num_files/count_of_docs)
            for x in self.index[key]:
                x.weight = (key[1] * x.tf_score) * x.multiplier
        
                
    def load_index(self):
        
        if os.path.isfile(self.INVERTED_INDEX_FILE_NAME):
            try:
                self.index = pickle.load(open(self.INVERTED_INDEX_FILE_NAME, "rb"))
                
            except:
                pass
        else:
            logger.info("No previous inverted index state found. Starting from the seed URL ...")

    def save_indexer(self):
    
        if not os.path.exists(self.INVERTED_INDEX_DIR_NAME):
            os.makedirs(self.INVERTED_INDEX_DIR_NAME)

        inverted_index_file = open(self.INVERTED_INDEX_FILE_NAME, "wb")
        pickle.dump(self.index, inverted_index_file)  
        
    
            