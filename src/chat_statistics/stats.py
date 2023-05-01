from typing import Union
from pathlib import Path
import json
from src.data import DATA_DIR
from hazm import word_tokenize, Normalizer, sent_tokenize
from wordcloud import WordCloud
import arabic_reshaper
from bidi.algorithm import get_display
from loguru import logger 
from collections import defaultdict, Counter


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
        stopwords = set(map(str.strip, stopwords))
        self.stopwords = set(map(self.normalize.normalize, stopwords))

    @staticmethod
    def rebuild_msg(sub_messages):
        msg_text = ' '
        for sub_msg in sub_messages:
            if isinstance(sub_msg, str):
                msg_text += sub_msg
            elif 'text' in sub_msg:
                msg_text += sub_msg['text']
        return msg_text

    def msg_has_questions(self, msg):
        """Checks if a mssage has a question
        :param msg: message to checks 
        """
        is_questions = defaultdict(bool)
        for msg in self.chat_data['messages']:
            if not isinstance(msg['text'], str):
                msg['text'] = self.rebuild_msg(msg['text'])

            sentences = sent_tokenize(msg['text'])
            for sentence in sentences:
                if ('?' not in sentence) and ('؟' not in sentence):
                    continue
                return True

    def get_top_users(self, top_10_users: int = 10):
        """Generate statistics from the chat data
        """
        # check messages for questions
        is_questions = defaultdict(bool)
        for msg in self.chat_data['messages']:
            if not isinstance(msg['text'], str):
                msg['text'] = self.rebuild_msg(msg['text'])

            sentences = sent_tokenize(msg['text'])
            for sentence in sentences:
                if ('?' not in sentence) and ('؟' not in sentence):
                    continue
                is_questions[msg['id']] = True
                break
        # get top users based on repling to questions from others
        logger.info(f"Getting  top {top_10_users} users... ")
        users = []
        for msg in self.chat_data['messages']:
            if not msg.get('reply_to_message_id'):
                continue

            if is_questions[msg['reply_to_message_id']] is False:
                continue
            users.append(msg['from'])

        top_10_users = dict(Counter(users).most_common(10))
        return top_10_users

    def generate_word_cloud(self, output_dir: Union[str, Path], width: int = 800, 
                            height : int = 600, max_font_size: int = 250):
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
            font_path=str(DATA_DIR/'BHoma.ttf'), width=1200, height=1200,
            max_font_size=200,
        ).generate(txt_cont)

        wordcloud.to_file(str(Path(output_dir) / 'wordcloud.png'))


if __name__ == "__main__":
    chat_stats = ChatStatistics(chat_json=Path(DATA_DIR / "result.json"))
    chat_stats.generate_word_cloud(output_dir=DATA_DIR)
    top_users = chat_stats.get_top_users(top_10_users=20)
    print(top_users)
    print('Done!')
