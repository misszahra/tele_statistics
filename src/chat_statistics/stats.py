from typing import Union
from pathlib import Path
import json
from src.data import DATA_DIR
from hazm import word_tokenize, Normalizer
from wordcloud import WordCloud
import arabic_reshaper
from bidi.algorithm import get_display
from loguru import logger 




class ChatStatistics:
    """Generates chat statistics from a telegram chat json file 
    """
    def __init__(self, chat_json: Union[str, Path]):
        """
        :param chat_json : path to telegram export json file
        """
        logger.info(f"Loding chat data from {chat_json}")
        with open(chat_json) as f:
            self.chat_data = json.load(f)

        self.normalize = Normalizer()
        # Load stopwords 
        logger.info(f"Loding stopword file from {DATA_DIR / 'stopwords.txt'}")
        stopwords = open(DATA_DIR / 'stopwords.txt').readlines()
        stopwords = list(map(str.strip, stopwords))
        self.stopwords = list(map(self.normalize.normalize, stopwords))

    def generate_word_cloud(self, output_dir: Union[str, Path]):
        """
        Generates a word cloud from the chat data 

         :param output_dir: path to output directory for word cloud imgage 
        """
        logger.info("Loding text content...")
        txt_cont = " "
        for msg in self.chat_data['messages']:
            if type(msg['text']) is str:
                tokens = word_tokenize(msg["text"])
                tokens = list(
                    filter(lambda item: item not in self.stopwords, tokens)
                    )        
                txt_cont += f" {' '.join(tokens)}"

        # Normaliz , reshpe for final word cloud 
        txt_cont = self.normalize.normalize(txt_cont[:1000])
        # txt_cont = arabic_reshaper.reshape(txt_cont)
        # txt_cont = get_display(txt_cont)

        # Generate word cloud 
        logger.info("Generating word cloud.... ")
        wordcloud = WordCloud(
            background_color='white',
            font_path= str(DATA_DIR/'BHoma.ttf'), 
            width=1200, 
            height=1200,
            max_font_size=200,
        ).generate(txt_cont)

        wordcloud.to_file(str(Path(output_dir) / 'wordcloud.png'))
if __name__=="__main__":
    chat_stats = ChatStatistics(chat_json=Path(DATA_DIR / "result.json"))
    chat_stats.generate_word_cloud(output_dir=DATA_DIR)

    print('Done !!!!!!!!!')
