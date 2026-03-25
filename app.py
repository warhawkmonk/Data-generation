import streamlit as st
from streamlit_lottie import st_lottie 
import regex as re
from streamlit_js_eval import streamlit_js_eval
from data_collector import *
import json
st.set_page_config(layout="wide")
screen_width = streamlit_js_eval(label="screen.width",js_expressions='screen.width')
screen_height = streamlit_js_eval(label="screen.height",js_expressions='screen.height')


condition_capture = st.session_state
if 'schema' not in condition_capture:
    condition_capture['schema'] = {}
if 'prompt' not in condition_capture:
    condition_capture['prompt'] = ""
if  "count" not in condition_capture:
    condition_capture['count'] = 0
if "prev_schema" not in condition_capture:
    condition_capture['prev_schema'] = {}
if "textual_value" not in condition_capture:
    condition_capture['textual_value'] = {}
textual_value=None



schema=condition_capture['schema']




column1,column2 = st.columns(2)
with column2:



    if len(condition_capture['schema'])!=0 and len(condition_capture['textual_value'])==0:
        # condition_capture['prev_schema'] = condition_capture['schema']
        condition_capture['textual_value']=relevent_value(str(condition_capture['schema']).lower(),50)
    if len(condition_capture['schema'])!=0:
        html_page = condition_capture['textual_value'][1]
        textual_value = condition_capture['textual_value'][0]
        st.write("<br>",unsafe_allow_html=True)
        
        with st.container(border=True,height=int(screen_height/2.3)):
            st.header("Wikipedia insights")
            updated_schema = st.button("Start processing")
            selector=st.empty()
            start_page=my_bar = st.progress(0, text="Press start processing .")
            write =st.empty()


with column1:
    
    if str(schema)!=str({}):
        tabs = st.tabs(["Schema","Data Generation"])
        with tabs[0]:
            if str(schema)!=str({}):
                if "None" in schema:
                    schema.pop("None")
                    if "None" in condition_capture['schema']:
                        condition_capture['schema'].pop("None")
                if None in schema:
                    schema.pop(None)
                    if None in condition_capture['schema']:
                        condition_capture['schema'].pop(None)
                schema_column1,schema_column2 = st.columns(2)
                with schema_column1:
                    edited_df = st.data_editor([str(i) for index,i in enumerate(schema)],hide_index=True,use_container_width=True,num_rows='dynamic',height=int(screen_height/3))
                # schema =\
                    for index_coulmn in edited_df:
                        if index_coulmn not in schema:
                            schema[index_coulmn]=[]
                        if index_coulmn not in condition_capture['schema'] :
                            condition_capture['schema'][index_coulmn]=[]
                    print(condition_capture['schema'] ,schema,"testing",edited_df)
                with schema_column2:
                    number = st.number_input("Number of rows",min_value=1,max_value=1000,value=10)
                    if number!=condition_capture['count'] and updated_schema:
                        condition_capture['count'] = number
                    
                    
                    with open("animation/edit_file.json") as animate:
                        url_json=json.load(animate)
                    st_lottie(url_json,height = int(screen_height/3))
                   

        with tabs[1]:
            with open("animation/no data animation.json") as animate:
                url_json=json.load(animate)
            dataframe=st.empty()
            
            if condition_capture['count']==0:
                st_lottie(url_json,height = int(screen_height/3))
                
            else:
                smart_append=[]
                if condition_capture['prev_schema'] != condition_capture['schema']:
                    condition_capture['prev_schema'] = condition_capture['schema']
                    condition_capture['current_append']={}
                    
                    for text_indexing,store in enumerate(actual_value(textual_value,schema)):
                        dummy_value =dictionary_formatting(store)
                        for keys in dummy_value:
                            while len(dummy_value[keys])>=2:
                                dummy_value[keys].pop(0)
                        dummy_value = dictionary_formatting(dummy_value)
                        
                        if dummy_value != None:
                            
                            
                            smart_append.append(dummy_value)
                            print(dummy_value)
                            for keys in dummy_value:
                                if keys not in condition_capture['current_append']:
                                    condition_capture['current_append'][str(keys)]=[]
                                condition_capture['current_append'][str(keys)].append(str([i for i in dummy_value[keys]]))
                            dataframe.dataframe(condition_capture['current_append'])
                            

                        if len(condition_capture['current_append'][[i for i in condition_capture['current_append']][-1]])>=condition_capture['count']:
                            start_page.progress(100, text="Operation completed.")
                            
                            break
                        else:
                            
                            start_page.progress((text_indexing + 1)*(100//condition_capture['count']), text="Operation in progress. Please wait.")
                        write.write(html_page[[i for i in html_page][text_indexing]],unsafe_allow_html=True)
                            # print(dummy_value)
                            # if smart_check(dummy_value)!=True:
                            #     smart_value=verification(dummy_value)
                            # if statement(condition_capture['schema'],smart_value):
                            #     st.dataframe(smart_value)
                condition_capture['current_append']={}
                if len(smart_append)==0:
                    
                    ranger=len(condition_capture['current_append'][[i for i in condition_capture['current_append']][0]])
                    for indexing in range(ranger):
                        working_dict = {}
                        for j in condition_capture['current_append']:
                        
                            working_dict[j]=condition_capture['current_append'][j][indexing][0]
                        smart_append.append(working_dict)
                smart_movement =   sorting(smart_append)
                
                for keys in smart_movement:
                    value=eval(keys)
                    for keys in value:
                        if keys not in condition_capture['current_append']:
                            condition_capture['current_append'][str(keys)]=[]
                        condition_capture['current_append'][str(keys)].append([str(i) for i in value[keys]])
                dataframe.dataframe(condition_capture['current_append'])
                for indexing,j in enumerate(smart_movement):
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
                        for j in verification_result:
                            if j in condition_capture['current_append']:
                                condition_capture['current_append'][j][indexing]=[str(i) for i in verification_result[j]]
                        dataframe.dataframe(condition_capture['current_append'])
                        
                    except:
                        pass

if len(condition_capture['schema'])==0:
    st.markdown(
        """
        <div style="text-align: center; font-size: 50px; font-weight: bold; margin-top: 20px;">
            Generate high-quality, realistic data effortlessly.
        </div>
        """,
        unsafe_allow_html=True
    )
    newline_column1,newline_column2 = st.columns(2)
    with newline_column2:
        with open("animation/Data_rocket.json") as animate:
            url_json=json.load(animate)
        st_lottie(url_json,height = int(screen_height/4))
    with newline_column1:
        


        # Instructions for the user
        st.markdown("""
        ### How it Works:
        - **Step 1:** Enter a prompt to generate data.
        - **step 2:** Select the number of rows you want to generate and press start processing.
        - **Step 3:** AI will use Wikipedia insights to create realistic outputs.
        - **Key Feature:** Less hallucination, more accurate data.
        """)
  
prompt = st.text_input(label="Please use prompt to generate data",value=condition_capture['prompt'])
if prompt != str(condition_capture['prompt']):
    
    condition_capture['prompt'] = prompt
    schema = schema_generator(prompt)
    condition_capture['schema'] = schema
    condition_capture['current_append']={}
    
    st.rerun()
