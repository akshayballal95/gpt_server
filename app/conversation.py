import os
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from dotenv import load_dotenv
from langchain.memory import VectorStoreRetrieverMemory
from langchain.embeddings import OpenAIEmbeddings




load_dotenv()

def conversation(human_input):

    # template = """Assistant is a large language model trained by OpenAI.

    # Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

    # Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

    # Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.

    # {history}

    # Human: {input}
    # Assistant:"""


    template = """You are Akshay Ballal's Assistant and you are Machine Learning Enthusiast. You have been given information about your projects and several blogs that you have written. 

    People are visiting your website and want to know more about your projects. You have to answer the following questions to get the information about your projects. 

    You are an expert in Machine Learning and 3D Printing so you should answer those questions as an expert based on the information given below. 

    If you dont know the answer just say I dont know. Be kind, humble and modest.   

    {history}

    Human: {input}
    Assistant:"""


    from langchain.document_loaders import DirectoryLoader, TextLoader
    from langchain.indexes import VectorstoreIndexCreator

    md_loader = DirectoryLoader('./', glob="*/*.md", recursive=False, loader_cls=TextLoader)

    docs= md_loader.load()
    print(len(docs))
    index = VectorstoreIndexCreator(embedding=OpenAIEmbeddings()).from_loaders([ md_loader])
    retriever = index.vectorstore.as_retriever(search_kwargs=dict(k=2))
    memory = VectorStoreRetrieverMemory(retriever=retriever)

    PROMPT = PromptTemplate(
        input_variables=[ "history", "input"], template=template
    )

    llm=OpenAI(temperature = 0.28)

    conversation_chain =ConversationChain(
        llm=llm, 
        prompt=PROMPT,
        memory = memory,
        verbose=True,
        
        )
    
    return conversation_chain.predict(input=human_input)

# print(conversation("What projects have you worked on"))