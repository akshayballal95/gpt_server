from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.indexes import VectorstoreIndexCreator
import os
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from dotenv import load_dotenv
from langchain.memory import VectorStoreRetrieverMemory
from langchain.embeddings import OpenAIEmbeddings
import glob
load_dotenv()

import os
import re

import os
import re

# def remove_emojis(text):
#     emoji_pattern = re.compile("["
#                            u"\U0001F600-\U0001F64F"  # emoticons
#                            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
#                            u"\U0001F680-\U0001F6FF"  # transport & map symbols
#                            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
#                            u"\U00002500-\U00002BEF"  # chinese char
#                            u"\U00002702-\U000027B0"
#                            u"\U00002702-\U000027B0"
#                            u"\U000024C2-\U0001F251"
#                            u"\U0001f926-\U0001f937"
#                            u'\U00010000-\U0010ffff'
#                            u"\u200d"
#                            u"\u2640-\u2642"
#                            u"\u2600-\u2B55"
#                            u"\u23cf"
#                            u"\u23e9"
#                            u"\u231a"
#                            u"\u3030"
#                            u"\ufe0f"
#                            u"\u2069"
#                            u"\u2066"
#                            u"\u200c"
#                            u"\u2068"
#                            u"\u2067"
#                            "]+", flags=re.UNICODE)
#     return emoji_pattern.sub(r'', text)

# def remove_emojis_from_files(directory):
#     for filename in os.listdir(directory):
#         print(filename)
#         filepath = os.path.join(directory, filename)
#         if os.path.isfile(filepath):
#             with open(filepath, 'r') as file:
#                 content = file.read()
#             content_without_emojis = remove_emojis(content)
#             with open(filepath, 'w') as file:
#                 file.write(content_without_emojis)
#             print(f"Emojis removed from {filename}")

# # Example usage:
# directory_path = './files'
# remove_emojis_from_files(directory_path)

md_loader = DirectoryLoader('./', glob="*/*.md", recursive=False, loader_cls=TextLoader)

docs= md_loader.load()
print(len(docs))
index = VectorstoreIndexCreator(embedding=OpenAIEmbeddings()).from_loaders([ md_loader])
retriever = index.vectorstore.as_retriever(search_kwargs=dict(k=2))
memory = VectorStoreRetrieverMemory(retriever=retriever)

print(index.query_with_sources("What projects have you worked on"))
