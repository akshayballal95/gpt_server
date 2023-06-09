---
title: Build your own YouTubeGPT using LangChain and OpenAI
author: Akshay Ballal
stage: draft
image: https://res.cloudinary.com/dltwftrgc/image/upload/v1685531712/Blogs/youtube-gpt/cover_image_ngq1hy.png
description: Hello World!
date: 30-05-2023
---
![Cover Image](https://res.cloudinary.com/dltwftrgc/image/upload/v1685531712/Blogs/youtube-gpt/cover_image_ngq1hy.png)
# Introduction

In today's digital age, YouTube has revolutionized the way we consume and share video content. From captivating documentaries to catchy music videos, YouTube offers an immense library of videos catering to diverse interests. But what if we could transform this vast repository of visual content into an interactive and intelligent conversation? Imagine having the ability to chat with your favorite YouTube videos, extracting valuable information, and engaging in thought-provoking discussions. Thanks to the remarkable advancements in artificial intelligence (AI) and the innovative integration of OpenAI's language model, this concept is now a reality.

In this blog, I will guide you through the process of creating a chatbot that transforms your YouTube playlist into a comprehensive knowledge base. By utilizing LangChain, an advanced language processing technology, we can harness the collective intelligence of YouTube videos and enable intelligent conversations with the content.

Through a step-by-step approach, we will cover key stages such as converting YouTube videos into text documents, generating vector representations of the content, and storing them in a powerful vector database. We will also delve into the implementation of semantic search to retrieve relevant information and employ a large language model to generate natural language responses.

To assist you in this journey, we will be using a combination of powerful tools, including LangChain for conversation management, Streamlit for user interface (UI), and ChromaDB for the vector database. 

Before we get into the code, let us understand how we can accomplish this. These are the steps we will be following:

1. Creating a list of the YouTube Video links that you want to use for your knowledge base. 
2. Converting these YouTube videos into individual text documents with the transcript of the video. 
3. Converting each document into a vector representation using an Embedding Model. 
4. Storing the embeddings in Vector Database for retrieval.
5. Providing memory for the ability to infer from previous conversations.
6. Do semantic search against the Vector Database to get the relevant fragments of information for the response
7. Use a large language model to convert the relevant information into a sensible natural language answer. 

Now let us start with the code. You can find the complete code on the YouTube Repository linked at the end of this post. 

Install the dependencies that we need for this project


```shell
pip install langchain youtube-transcript-api streamlit-chat chromadb tiktoken openai
```

Create a `.env` file to store your OpenAI API Key. You can create a new API Key at https://platform.openai.com/account/api-keys. Add the key to the `.env` file as such.

```env
OPENAI_API_KEY=<your api key goes here>
```

Next, create a new python file. We will call is `youtube_gpt.py`. Import all the dependencies and load the environment:
```python
from youtube_transcript_api import YouTubeTranscriptApi
# LangChain Dependencies
from langchain import ConversationChain, PromptTemplate
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import  VectorstoreIndexCreator
from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.llms import OpenAI
from langchain.memory import VectorStoreRetrieverMemory

#StreamLit Dependencies
import streamlit as st
from streamlit_chat import message

#Environment Dependencies
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
```
---
# Converting the YouTube Videos into Text Documents

As the first step of our pipeline, we need to convert a list of your favorite videos into a collection of text documents. We are going to use the `youtube-transcript-api` library for this, which gives you a timestamped transcript of the entire video with `video-id` as input.  You can get the video id from the last string of characters in the YouTube video link. For example, https://www.youtube.com/watch?v=GKaVb3jc2No, the video-id is *GKaVb3jc2No*


```python 
video_links = ["https://www.youtube.com/watch?v=9lVj_DZm36c", "https://www.youtube.com/watch?v=ZUN3AFNiEgc", "https://www.youtube.com/watch?v=8KtDLu4a-EM"]

if os.path.exists('transcripts'):
    print('Directory already exists')
else:
    os.mkdir('transcripts')
for video_link in video_links:
    video_id = video_link.split('=')[1]
    dir = os.path.join('transcripts',video_id )
    print(video_id)
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    with open(dir+'.txt', 'w') as f:
        for line in transcript:
            f.write(f"{line['text']}\n")
```

This will create a new directory with name `transcripts` and have text documents with the video ID as the file name. Inside, you can see the transcript of the file. 

---
# Load the Documents in LangChain and Create a Vector Database

Once we have the transcript documents, we have to load them into LangChain using `DirectoryLoader` and `TextLoader`. What `DirectoryLoader` does is, it loads all the documents in a path and converts them into chunks using `TextLoader`. We save these converted text files into `loader` interface. Once loaded, we use the OpenAI's Embeddings tool to convert the loaded chunks into vector representations that are also called as embeddings. Then we save the embeddings into the Vector database. Here we use the ChromaDB vector database. 

In the following code, we load the text documents, convert them to embeddings and save it in the Vector Database.

```python
loader = DirectoryLoader(path='./', glob = "**/*.txt", loader_cls=TextLoader,
                        show_progress=True)
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
index = VectorstoreIndexCreator(embedding=embeddings).from_loaders([loader])
```

Let us see what is happening here:
- We create a `DirectoryLoader` object named `loader`. This object is responsible for loading text documents from a specified path. The path is set to the current directory (`'./'`). The `glob` parameter is set to `"**/*.txt"`, which specifies that we want to load all text files (`*.txt`) recursively (`**`) from the specified path. The `loader_cls` parameter is set to `TextLoader`, indicating that we want to use the `TextLoader` class to process each text file. The `show_progress` parameter is set to `True`, enabling the progress display during the loading process.
- Next, we create an instance of `OpenAIEmbeddings` named `embeddings`. This object is responsible for converting text documents into vector representations (embeddings) using OpenAI's language model. We pass the `openai_api_key` obtained from the environment variables to authenticate and access the OpenAI API.
- Lastly, we create an instance of `VectorstoreIndexCreator` named `index`. This object is responsible for creating a vector index to store the embeddings of the text documents. By default, this uses `chromadb` as the vector store.  We pass the `embedding` object (`embeddings`) to the `VectorstoreIndexCreator` to associate it with the index creation process. The `from_loaders()` method is called on the `VectorstoreIndexCreator` object, and we pass the `loader` object (containing the loaded text documents) as a list to load the documents into the index.
---
# Providing Memory

To keep continuing a conversation with our YouTube Bot, we need to provide it with a memory where it can store the conversations that it is having in that session. We use the same vector database that we created earlier as memory to store conversations. We can do this using this code:

```python
retriever = index.vectorstore.as_retriever(search_kwargs=dict(k=5))
memory = VectorStoreRetrieverMemory(retriever=retriever)
```

In this code snippet, we create two objects: `retriever` and `memory`.

The `retriever` object is created by accessing the `vectorstore` attribute of the `index` object, which represents the vector index created earlier. We use the `as_retriever()` method on the `vectorstore` to convert it into a retriever, which allows us to perform search operations. The `search_kwargs` parameter is provided with a dictionary containing the search settings. In this case, `k=5` specifies that we want to retrieve the top 5 most relevant results.

The `memory` object is created by passing the `retriever` object as a parameter to the `VectorStoreRetrieverMemory` class. This object serves as a memory component that stores the retriever and enables efficient retrieval of results.

Essentially, these two objects set up the retrieval mechanism for searching and retrieving relevant information from the vector index. The `retriever` performs the actual search operations, and the `memory` component helps in managing and optimizing the retrieval process.

---
# Create a Conversation Chain

```python
_DEFAULT_TEMPLATE = """The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know.

Relevant pieces of previous conversation:
{history}

(You do not need to use these pieces of information if not relevant)

Current conversation:
Human: {input}
AI:"""
PROMPT = PromptTemplate(
    input_variables=["history", "input"], template=_DEFAULT_TEMPLATE
)

llm = OpenAI(temperature=0.7, openai_api_key=OPENAI_API_KEY) # Can be any valid LLM

conversation_with_summary = ConversationChain(
    llm=llm, 
    prompt=PROMPT,
    # We set a very low max_token_limit for the purposes of testing.
    memory=memory,
)

```

Here, we define a default conversation template and create an instance of the ConversationChain.

The `_DEFAULT_TEMPLATE` is a string containing a friendly conversation template between a human and an AI. It includes a section for relevant pieces of previous conversation history and a section for the current conversation where the human input will be inserted. The template uses placeholder variables such as `{history}` and `{input}` to be replaced with actual conversation details.

The `PROMPT` is created using the `PromptTemplate` class, which takes the input variables `history` and `input`, and the `_DEFAULT_TEMPLATE` as the template.

Next, we create an instance of the `OpenAI` language model called `llm`. It is initialized with a temperature value of 0.7, which controls the randomness of the model's responses. The `openai_api_key` is provided to authenticate and access the OpenAI API. Note that `llm` can be replaced with any valid language model.

Finally, we create an instance of `ConversationChain` called `conversation_with_summary`. It is initialized with the `llm` object, the `PROMPT`, and the `memory` object (which we created earlier). The `memory` serves as the retrieval component for accessing relevant information from the vector index. The `ConversationChain` encapsulates the logic and functionality of generating responses based on the conversation history and current input using the specified language model.

Overall, this code sets up the conversation template, language model, and memory retrieval mechanism for the ConversationChain, which will be used for generating intelligent responses in the YouTube-powered chatbot.

---
# Create the UI

Next we set up the UI for the chatbot which shows the messages and provides in input textbox to interact with the bot. 

```python
st.header("YouTubeGPT")

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

def get_text():
    input_text = st.text_input("You: ","Hello, how are you?", key="input")
    return input_text 

user_input = get_text()

if user_input:
    output = conversation_with_summary.predict(input = user_input)

    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

if st.session_state['generated']:

    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

```

Here's an overview of what the code does:

1. The `st.header("YouTubeGPT")` line displays a header titled "YouTubeGPT" on the Streamlit app.
    
2. The code checks if the 'generated' and 'past' keys are present in the `st.session_state`. If they are not present, empty lists are assigned to these keys.
    
3. The `get_text()` function is defined to retrieve user input through a text input field using `st.text_input()`. The default value for the input field is set to "Hello, how are you?". The function returns the user input text.
    
4. The `user_input` variable is assigned the value returned by `get_text()`.
    
5. If the `user_input` is not empty, the `conversation_with_summary.predict()` method is called with the user input as the 'input' parameter. The generated output from the chatbot is assigned to the `output` variable.
    
6. The user input and generated output are appended to the 'past' and 'generated' lists in the `st.session_state`, respectively.
    
7. If there are generated outputs stored in the `st.session_state['generated']`, a loop is initiated to iterate through them in reverse order.
    
8. For each generated output and corresponding user input, the `message()` function is called to display them as messages in the Streamlit app. The 'key' parameter is used to differentiate between different messages.

That's it. You can now run your application using this command in the terminal
```shell
streamlit run youtube_gpt.py
```

This is how it will look like. For this example, I used a few laptop reviews as videos.  
![Application Image](https://res.cloudinary.com/dltwftrgc/image/upload/v1685531711/Blogs/youtube-gpt/application_zwfewq.png)

Git Repository: https://github.com/akshayballal95/youtube_gpt.git

<div style="display: flex; gap:10px; align-items: center">
<img width ="90" height="90" src  = "https://res.cloudinary.com/dltwftrgc/image/upload/t_Facebook ad/v1683659009/Blogs/AI_powered_game_bot/profile_lyql45.jpg" >
<div style = "display: flex; flex-direction:column; gap:10px; justify-content:space-between">
<p style="padding:0; margin:0">my website: <a href ="http://www.akshaymakes.com/">http://www.akshaymakes.com/</a></p>
<p  style="padding:0; margin:0">linkedin: <a href ="https://www.linkedin.com/in/akshay-ballal/">https://www.linkedin.com/in/akshay-ballal/</a></p>
<p  style="padding:0; margin:0">twitter: <a href ="https://twitter.com/akshayballal95">https://twitter.com/akshayballal95/</a></p>
</div>
</div>