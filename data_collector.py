
import wikipedia
import wikipediaapi
import regex as re
from sentence_transformers import SentenceTransformer,util
from transformers import pipeline
import requests

def consume_llm_api(prompt):
    """
    Sends a prompt to the LLM API and processes the streamed response.
    """
    url = "http://127.0.0.1:6000/api/llm-response"
    headers = {"Content-Type": "application/json"}
    payload = {"prompt": prompt,"extension":"1"}

    
    print("Sending prompt to the LLM API...")
    response_ = requests.post(url, json=payload,verify=False)
    response_data = response_.json()
    print(response_data)
    return response_data['text']
# def consume_llm_api(prompt):

#     import requests
#     from sentence_transformers import SentenceTransformer
#     from pinecone import Pinecone, ServerlessSpec
#     Gen_api = "https://8417-201-238-124-65.ngrok-free.app/api/llm-response"
#     api_key = "pcsk_2EhvKP_GqGkpAjF4p4ziL7PgrgM9xuKcthX9gtqhyLxV3UaMmWTQufW4qKZrjhLrf2d1ma"
#     pc = Pinecone(api_key=api_key)
#     model = SentenceTransformer("all-mpnet-base-v2")
#     try:
#         index_name = "quickstart"
#         pc.create_index(
#             name=index_name,
#             dimension=768, 
#             metric="cosine", 
#             spec=ServerlessSpec(
#                 cloud="aws",
#                 region="us-east-1"
#             ) 
#         )
#     except:
#         pass
#     index = pc.Index(index_name)
#     index.upsert(
#         vectors=[
#             {
#                 "id": "lorum", 
#                 "values": [float(i) for i in list(model.encode("lorum"))],  
#                 "metadata": {"string":str(prompt)}
                
#             }
#         ]
#     )

#     gen_api_response = requests.post(url = Gen_api,json={"api_key": api_key},verify=False)

#     if gen_api_response.json().get("status"):
#         response = index.query(
#         vector=[float(i) for i in model.encode(str(prompt))],
#         top_k=1,
#         include_metadata=True,
#     )

        
#     return response['matches'][0]['metadata']['string']


def relevent_value(long_query,count=3):
    results = wikipedia.search(long_query,results=count)
    
    wiki_wiki = wikipediaapi.Wikipedia(user_agent='MyProjectName (merlin@example.com)', language='en',extract_format=wikipediaapi.ExtractFormat.WIKI)
    wiki_wiki_html = wikipediaapi.Wikipedia(user_agent='MyProjectName (merlin@example.com)', language='en',extract_format=wikipediaapi.ExtractFormat.HTML)
    values={}
    html_values={}
    for result in results:
        page_py = wiki_wiki.page(result)
        page_html = wiki_wiki_html.page(result)
        html_values[result]=page_html.text

        values[result]=page_py.text
    return values,html_values


from langchain_community.llms import Ollama
model=Ollama(model="llama3:latest",temperature=0.3)
# agent_understanding = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
# qa_model = pipeline('question-answering', model='deepset/roberta-base-squad2', tokenizer='deepset/roberta-base-squad2')

# textual_value

def construction_edit(textual_value,schema):
    construction_prompt= textual_value+"\n"
    construction_prompt+="Above is the generated text from wikipedia and below is the rule that has to be filled in the data. \n"
    construction_prompt+="The data should be in the form of a dictionary and it must follow the following schema: \n"
    construction_prompt+=str(schema)+"\n"
    construction_prompt+="The length of each list of each key must be same in the generated data(mandatory)."+"\n"
    construction_prompt+="No helper text like 'Here is the filled-in JSON schema based on the provided text' or 'Note: I've filled in the keys with relevant data' ."+ "\n"
    construction_prompt+="The output must be a dictionary"+"\n"
    constructed_text=consume_llm_api(construction_prompt)
    return constructed_text

def dictionary_check(construction_edit):
    for keys in construction_edit:
        if len(construction_edit[keys])==0:
            return False
    return True

def actual_value(textual_value,schema):
    for j in textual_value:
        formatted_result = str(textual_value[j])+ "\n"
        formatted_result += "Please fill the following schema with the relevant data from the text above."+ "\n"
        formatted_result += "Here is the schema"+"\n"
        formatted_result += str(schema)
        formatted_result += "Please generate data according to schema and fill this template with your answers.\n"
        formatted_result += "You have to fill each key with the relevant data from the text above."+ "\n"
        formatted_result += "Please return the exact key value pair as the schema above. "+ "\n"
        formatted_result += "No helper text like 'Here is the filled-in JSON schema based on the provided text' or 'Note: I've filled in the keys with relevant data' ."+ "\n"
        formatted_result += "Only fill the keys that are in the schema."+ "\n"
        formatted_result += "If you are not sure about the data, you can add 'Na'."+ "\n"
        formatted_result += "It's an order you can not add any other text(e.g Here is the filled-in JSON schema) or note ."+ "\n"
        formatted_result += "The length of each list of each key must be same in the generated data(mandatory)."+"\n"
        raw_output = consume_llm_api(formatted_result)
        try:
            data=construction_edit(raw_output,schema)
            json_object_match = re.search(r'\{(?:[^{}]|(?R))*\}', data)
            access_value=eval(json_object_match.group())
            for schema_key in schema:
                if schema_key not in access_value:
                    access_value[schema_key]=list(set())
            for schema_key in access_value:
                access_value[schema_key]=list(set(access_value[schema_key]))
                access_value[schema_key]=list(set(access_value[schema_key])-set(["Na"]))
            yield access_value
            
        except:
            access_value=None
        



def context_data_relevancy(value,context):
    researcher =  "You are a professional reasearcher from data ."+ "\n"
    researcher += "You have to check can we fill some of the missing values in the "+str(value) + ". \n"  
    researcher += "The possible part which available in the context has to be relevent with already present data"+ ". \n"
    researcher += "from the context given below"+ ". \n"
    researcher += context+ "\n"
    researcher += "Be strict while thing of filling data"+ ". \n"
    researcher += "Just return @yahoo@ if 90% possible else @NO@"+ ". \n"


    result = consume_llm_api(researcher)
    return result

def agent_work_result(query,value):
    agent_understanding = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    query_embedding = agent_understanding.encode(query)
    score1 = util.cos_sim(query_embedding,agent_understanding.encode("extract data for"))
    score2 = util.cos_sim(query_embedding,agent_understanding.encode("append data in "))
    score3 = util.cos_sim(query_embedding,agent_understanding.encode("check data"))

    if score1 > score2 and score1 > score3:
        # print("Extracting query:", query)
        question = "search word ?"
        result = qa_model(question=question, context=query)
        result = result['answer']
        print("Extracting query:", result)
        wikisearch = relevent_value(result,3)
        html_pages = wikisearch[1]
        wikisearch = wikisearch[0]

        for searches in wikisearch:
            if "@yahoo@" in context_data_relevancy(value,wikisearch[searches]):
                return wikisearch[searches]
        return "No data found"
    elif score2 > score1 and score2 > score3:
        try:
            print("Appending command:", query)
            question1 = "which value we are adding to key ?"
            result1 = qa_model(question=question1, context=query)
            question2 = "In which key we are appending ?"
            result2 = qa_model(question=question2, context=query)
            result1 = result1['answer']
            result2 = result2['answer']

            if  len(value[result2])==0:
                value[result2].append(result1)
                return "Now you can fill the remaining columns"
            else:
                return "You are putting value in the same key column again not accepted."
        except Exception as e:
            return str(e)
    else:
        min_=0
        max_=0
        for keys in value:
            
            if len(value[keys])<min_:
                min_=len(value[keys])
            if len(value[keys])>max_:
                max_=len(value[keys])
        if min_==max_:
            return "You dia a great job"
        else:
            return "Please append the data correctly so that the length of each key is same and data is also relevant"
    

def full_alignment(value):
    for values in value:
        if len(value[values])==0:
            return False
    return True

def query_formatting(result):
    values=result.split("\n")
    if len(values)!=0:
        values.pop(0)
    return values
def missing_value_completion(store,value):

    filler_prompt = "Below is mentioned ajson data\n"
    filler_prompt += str(value)+"\n"
    filler_prompt += "you only need to find missing data from the mentioned context section."
    filler_prompt += "You will return the results in below mentioned format.\n"
    filler_prompt += "The output will be in json format."
    filler_prompt += "context:\n"
    
    for search_key in store:
        try:
            fill_text = store[search_key]
            response = consume_llm_api(filler_prompt+fill_text)
        
            json_object_match = re.search(r'\{(?:[^{}]|(?R))*\}', response)
            access_value=eval(json_object_match.group())
            for keys in value:
                if len(value[keys])==0 and keys in access_value:
                    value[keys].append(access_value[keys].pop(0))
            print(value)
            if full_alignment(value):
                return value
        except:
            pass
        



def verification(value):
    

    validation_prompt = "Can you prepare a list of text(many as possible) that can be searched on google for filling(relevent data) the missing data below.\n"
    validation_prompt += str(value)+"\n"
    validation_prompt += "You need to prepare it by the following manner"
    validation_prompt += "1. Mention it line by line.\n"
    validation_prompt += "2. Please seperate it line by line.\n"
    validation_prompt += "3. Headers are not required\n"
    validation_prompt += "4. Please do not add any helper text example: Here is the required search queries , Here are the search queries .\n"
    validation_prompt += "5. Please do not add any notes"
    print("Searching for missing values")
    result=query_formatting(consume_llm_api(validation_prompt))

    for search_queries in result:
        if len(search_queries)!=0:
            print(search_queries)
            store=relevent_value(search_queries)
            html_pages = store[1]
            store = store[0]
            missing_value_completion(store,value)
        if full_alignment(value):
            return value

            



    return result

def agent_data_prep(value,query):
    end_result = ""
    angent_earlier_income ="0"
    pre_money_saving = "0"
    mission = "First to fill most importent column \n"
    while end_result!="You dia a great job":
        
        if full_alignment(value):
            return value
            

        agent_instruction = mission
        agent_instruction += "your previous income"+pre_money_saving+"\n"
        agent_instruction += "your current income"+angent_earlier_income+"\n"
        pre_money_saving = angent_earlier_income
        if end_result=="You are putting value in the same key column again not accepted.":
            
            mission = "Why you are always filling the"+[i for i in value][-1]+"only.\n"
            mission += "We are removing $1000 from you account \n"
            angent_earlier_income = str(int(angent_earlier_income)-1000)
        agent_instruction += end_result + "\n" +"Above is the result of your previous command. Please give the next command to the agent."
        agent_instruction += query  + "\n"
        agent_instruction += "Below is the data gathered upto now" + "\n"
        agent_instruction += str(value) + "\n"
        agent_instruction += "Please utilize the tool where you can command the agent to do any of the following tasks(one instruction at a time )"+ "\n"
        agent_instruction += "You only have to fill one value for each key if its not present. \n"
        agent_instruction += "From now onwards your each statement is understand as command which is categoried in any of the commands in mentioned below examples. \n"
        agent_instruction += "1. Ask agent to extract data from the web about anything like search for lamp production ,smartphone parts etc .\n"
        agent_instruction += "2. Give any specific value to append in current generated data . Please also mention the key in which the agent has to append the data .\n"
        agent_instruction += "3. Ask the agent to put the generated data on check weather each column fills correctly or not .\n"
        agent_instruction += "Here is the instruction to give commands to the agent. \n"
        agent_instruction += "You can give commands to the agent ,few examples are mentioned below. \n"
        
        agent_instruction += "1. Extract data about iron man suit  or iron man suit mark1 \n"
        agent_instruction += "(while thinking about extract data look into the data \n"
        agent_instruction += "where data can be append and then search relevent query \n"
        agent_instruction += "like green arrow from DC only if DC and green arraow is in different column key values )\n\n"

        agent_instruction += "2. Append value 'bmw 4' to Car Model key \n"
        agent_instruction += "(While appending the value you must have read the data from extract data command and remember, if you found anything relevent don't forget to append.\n"
        agent_instruction += "The appending value has to be different not already present.) \n\n"
            
        agent_instruction += "Any different grammatical version of the above commands. \n"
        agent_instruction += "Command has to be given only for 'data filling' purpose. \n"

        agent_instruction += "While command like search for or extract information about something it has to be relevent query search. \n"
        agent_instruction += "The relevent the query the more accurate the data will be. \n"
        agent_instruction += "Be cautious while filling the data It has to be correct. \n"
        agent_instruction += "For each correct append you will get $1000. \n"

        agent_instruction += "Give your command only no text . \n"

        agent_instruction += "There will an audit after filling all the columns on data for its validity. \n"
        agent_instruction += "Some mistakes are okay but But if we find you guilty there are some repercussion."

        # instructionto give commands to the agent

        judgement = Ollama(model = "llama3:latest")
        command = judgement.invoke(agent_instruction)
        
        end_result = agent_work_result(command,value)
        if "Now you can fill the remaining columns" in end_result:
            angent_earlier_income = str(int(angent_earlier_income)+1000)
        print("--------------------")
        print(value)
        print("--------------------")
    return value

def dictionary_formatting(value):
    new_dict={}
    for data_keys in [i for i in value]:
        key_values = data_keys.strip()
        if key_values in value:
            if key_values not in new_dict:
                new_dict[key_values] =[]
            new_dict[key_values] = value.pop(key_values)
        else:
            new_dict[key_values] = value.pop(data_keys)
    return new_dict
            
        
def schema_formatter(output):
    schema = {i:[] for i in output.split(",")}
    return schema
def schema_generator(query):
    
    formatting = "The above statement is given by the user. Please create a single .csv-based schema by following the points below:\n"

    formatting += "1. Only create the schema, no additional text or statement.\n"

    formatting += "2. Keep the schema simple, avoid complex column names.\n"

    formatting+=  "3. please only generate 5 schema if not mentioned.\n"

    formatting += "4. For example, if the user provides a statement like: 'Generate data for students getting placements from IIT Bombay,' the response should be:\n"

    formatting += "Student Name, Student Roll Number, Student Branch, Student Year, Student Placement Status, Student Company Name, Student Package, Student Location, Student Role\n"

    formatting += "Follow the above example but remember above is not actual schema you have to provide the schema depending on the user prompt.\n"

    formatting+=  "5. please only generate schema no notes or anything.\n"

    output=consume_llm_api(query+"\n"+formatting)

    return schema_formatter(output)
def sorting(data_dict):
    new_dict={str(i):0 for i in data_dict}

    for i in data_dict:
        for j in i:
            if len(i[j])!=0:
                new_dict[str(i)] +=1
    new_dict=[(new_dict[i],i) for i in new_dict]
    new_dict.sort(reverse=True)
    new_dict={i[-1]:i[0] for i in new_dict}
    return new_dict


def process_data(query):

    
        

        formatting = "The above statement is given by the user. Please create a single .csv-based schema by following the points below:\n"
        formatting += "1. Only create the schema, no additional text or statement.\n"
        formatting += "2. Keep the schema simple, avoid complex column names.\n"
        formatting+=  "3. please only generate 5 schema if not mentioned.\n"
        formatting += "4. For example, if the user provides a statement like: 'Generate data for students getting placements from IIT Bombay,' the response should be:\n"
        formatting += "Student Name, Student Roll Number, Student Branch, Student Year, Student Placement Status, Student Company Name, Student Package, Student Location, Student Role\n"
        formatting += "Follow the above example but remember above is not actual schema you have to provide the schema depending on the user prompt.\n"
        formatting+=  "5. please only generate schema no notes or anything.\n"
        print("Query:",query)
        output=consume_llm_api(query+"\n"+formatting)

        schema = {i:[] for i in output.split(",")}
        textual_value=relevent_value(str(schema).lower(),3)
        html_pages = textual_value[1]
        textual_value = textual_value[0]
        data_dict =[j for j in actual_value(textual_value,schema)]
        for j in sorting(data_dict):
            try:
                # Convert string to dictionary
                dummy_value = eval(j)
                
                # Process dictionary values
                for key in dummy_value:
                    while len(dummy_value[key]) >= 2:
                        dummy_value[key].pop(0)
                
                # Format dictionary
                formatted = dictionary_formatting(dummy_value)
                print(formatted)
                # Verify and store result
                verification_result = verification(formatted) if formatted else None
                
                yield verification_result
                
            except Exception as e:
                print(f"Error processing dictionary {j}: {e}")