from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")

def generate_ticket_summary(chat_responses):
    """
    Generate a summary of the user's issue based on chat responses.
    
    Parameters:
    chat_responses (dict): Dictionary containing the user's responses at each step
    
    Returns:
    str: A formatted summary of the issue for ticket creation
    """
    
    sysTemplate = "You are given the questions and the response given by a user about the issue they are facing. Now you need to summarize the user's issue, such that no important detail is missed. And your response should only contain the summary of the user's issue, no other text should be present."

    promptTemplate = ChatPromptTemplate.from_messages([
    ("system", sysTemplate),
    ("human", "Question 1 : 'Hello! Could you please describe the issue you're experiencing with our app?', Response : '{detail_1}', Question 2 : 'What specific transaction or service were you using when you encountered the issue?', Response : '{detail_2}', Question 3 : When did you first notice this problem, and has it happened before?, Response : '{detail_3}', Question 4 : 'Did you see any error messages or unusual notifications? If so, please share the details, along with information about your device or network if possible.', Response : '{detail_4}'")
    ])
    
    
    getPrompt = RunnableLambda(lambda x : promptTemplate.invoke(x))
    callModel = RunnableLambda(lambda x : model.invoke(x))
    getResult = RunnableLambda(lambda x : x.content)
    
    chain = getPrompt | callModel | getResult
    
    detail_1 = chat_responses.get('step_0', 'No issue specified')
    detail_2 = chat_responses.get('step_1', 'General')
    detail_3 = chat_responses.get('step_2', 'Medium')
    detail_4 = chat_responses.get('step_3', 'No additional details provided')
    
    summary = chain.invoke({"detail_1" : detail_1, "detail_2" : detail_2, "detail_3": detail_3, "detail_4" : detail_4})
    
    return summary

def get_title(summary):
    
    sysTemplate = "You are given the summary for an user's issue, now you need to determine a brief, to the point title for the issue. Your response should contain only the title, no other text should be present."

    promptTemplate = ChatPromptTemplate.from_messages([
    ("system", sysTemplate),
    ("human", "Here is the summary : '{summary}'")
    ])
    
    
    getPrompt = RunnableLambda(lambda x : promptTemplate.invoke(x))
    callModel = RunnableLambda(lambda x : model.invoke(x))
    getResult = RunnableLambda(lambda x : x.content)
    
    chain = getPrompt | callModel | getResult
    
    title = chain.invoke({"summary" : summary})
    
    return title

def get_category(summary):
    
    sysTemplate = "You are given the summary for an user's issue, now you need to determine the category of the issue. Here are the available categories : Payments, Transfers, Accounts, Security, Refunds. Choose the category, and your response should contain only one word, that is the category."

    promptTemplate = ChatPromptTemplate.from_messages([
    ("system", sysTemplate),
    ("human", "Here is the summary : '{summary}'")
    ])
    
    
    getPrompt = RunnableLambda(lambda x : promptTemplate.invoke(x))
    callModel = RunnableLambda(lambda x : model.invoke(x))
    getResult = RunnableLambda(lambda x : x.content)
    
    chain = getPrompt | callModel | getResult
    
    category = chain.invoke({"summary" : summary})
    
    return category

def get_priority(summary, category):
    
    sysTemplate = "You are given the summary for an user's issue and the category it falls under, now you need to determine the priority of the issue. Here are the available priorities : Low, Medium, High. Choose the category, and your response should contain only one word, that is the priority."

    promptTemplate = ChatPromptTemplate.from_messages([
    ("system", sysTemplate),
    ("human", "Here is the summary : '{summary}'\nand here is the catgory : '{category}'")
    ])
    
    
    getPrompt = RunnableLambda(lambda x : promptTemplate.invoke(x))
    callModel = RunnableLambda(lambda x : model.invoke(x))
    getResult = RunnableLambda(lambda x : x.content)
    
    chain = getPrompt | callModel | getResult
    
    priority = chain.invoke({"summary" : summary, "category" : category})
    
    return priority

def get_potential_cause(summary, category, log_data) :
    
    sysTemplate = "You are given the summary for an user's issue, the category it falls under and the log data of the user. Now you need to determine the potential cause of the issue by analyzing the log data along with the provided summary. Your response should contain a detailed summary of the potential cause of the issue, and it should contain each and every detail like timestamp and all. Importantly, your response should only contain the cause paragraph, nothing else."

    promptTemplate = ChatPromptTemplate.from_messages([
    ("system", sysTemplate),
    ("human", "Here is the summary : '{summary}'\nand here is the catgory : '{category}', Here is the lod data for the user : {log_data}")
    ])
    
    
    getPrompt = RunnableLambda(lambda x : promptTemplate.invoke(x))
    callModel = RunnableLambda(lambda x : model.invoke(x))
    getResult = RunnableLambda(lambda x : x.content)
    
    chain = getPrompt | callModel | getResult
    
    cause = chain.invoke({"summary" : summary, "category" : category, "log_data" : log_data})
    
    return cause