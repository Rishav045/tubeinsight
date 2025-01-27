from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from youtube_transcript_api import YouTubeTranscriptApi
# import google.generativeai as genai
# model = genai.GenerativeModel('gemini-pro')
import pathlib
import textwrap
import os
# from IPython.display import display
from IPython.display import Markdown
import requests
from openai import OpenAI 
from dotenv import load_dotenv
import math

load_dotenv()
# MODEL="gpt-4o-mini"
# client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY") )
MODEL="deepseek-chat"
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),base_url="https://api.deepseek.com" )
def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

def url_to_code(url):
    code=""
    if(url.find("www.youtube.com")!=-1):
        print("running")
        for i in range(url.find('v=')+2,len(url)):
            if(url[i]=='&'):
                break
            else:
                code = code+url[i]
    elif(url.find("youtu.be")!=-1):
        print(url.find("youtu.be"))
        for i in range(url.find("youtu.be")+9,len(url)):
            if(url[i]=='?'):
                break
            else:
                code = code + url[i]
    else:
        # print("I am here")
        return("blank")
    return(code)
def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

def getYoutubeScript1(code : str = None):
    print("running new one")
    url = "https://youtube-transcriptor.p.rapidapi.com/transcript"

    headers = {
    # "X-RapidAPI-Key": "05f93faddamsh06e8d213053c0f4p13558bjsne63c2384e3ca",
    "X-RapidAPI-Key":os.getenv("X_RAPID_API_KEY"),
    "X-RapidAPI-Host": os.getenv("X_RAPID_API_HOST")
    }
    transcript=""
    code=url_to_code(code)
    if(code=="blank"):
        return {"message":"Please enter correct URL "}
    querystring = {"video_id":code}

    response = requests.get(url, headers=headers, params=querystring)
    # print(response.json())
    try:
        for content in response.json()[0]['transcription']:
            transcript = transcript + str(content['subtitle'])+" "
    except KeyError as Ie:
        print(f"Index error {Ie}")
        return {"message":"No Script available for this video"}
    return response.json()

def get_seconds(hour , minute , second):
    total_minute=(hour)*60+minute
    total_seconds=(total_minute)*60+second
    return total_seconds

def get_scripts_by_timing(code,start_time=[],end_time=[]):
    scripts=getYoutubeScript1(code)
    # print(scripts[0])
    start_seconds=get_seconds(int(start_time[0]),int(start_time[1]),int(start_time[2]))
    global end_seconds
    end_seconds=get_seconds(int(end_time[0]),int(end_time[1]),int(end_time[2]))
    if start_seconds > int(scripts[0]['lengthInSeconds']):
        print(f"Start time is greater than the end time of the video \n Total duration of the video is :- {scripts[0]['lengthInSeconds']}") 
    if len(start_time)==0 and len(end_time)==0:
        start_seconds=0
        end_seconds=scripts[0]['lengthInSeconds']
    transcript_entry=[]
    for entry in scripts[0]['transcription']:
        # If start is greater than the start_seconds and less than or equal to end_seconds
        s_compare=start_seconds-1
        if (s_compare<0):
            s_compare=0
        if entry['start']>=s_compare and math.ceil(entry['start'])<=end_seconds:
            transcript_entry.append(entry)
    transcript=""
    for entry in transcript_entry:
        transcript=transcript+" "+entry['subtitle']
    # print(transcript_entry)

    return {"Title":scripts[0]['title'],"Description":scripts[0]['description'].split('\n')[0],"Scripts":transcript}

app = FastAPI()

origins =[
    "https://ashishrnx.github.io",
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
)

@app.get('/')
def root():
    return {"Message":"Hello World"}
@app.get('/content/')
def getYoutubeScript(code : str = None):
    url = "https://youtube-transcriptor.p.rapidapi.com/transcript"


    print(code)
    headers = {
    # "X-RapidAPI-Key": "05f93faddamsh06e8d213053c0f4p13558bjsne63c2384e3ca",
    "X-RapidAPI-Key":os.getenv("X_RAPID_API_KEY"),
    "X-RapidAPI-Host": os.getenv("X_RAPID_API_HOST")
    }
    transcript=""
    code=url_to_code(code)
    
    if(code=="blank"):
        return {"message":"Please enter correct URL "}
    querystring = {"video_id":code}

    response = requests.get(url, headers=headers, params=querystring)
    print(response.json())
    try:
        for content in response.json()[0]['transcription']:
            transcript = transcript + str(content['subtitle'])+" "
    except KeyError as Ie:
        print(f"Index error {Ie}")
        return {"message":"No Script available for this video"}
    return transcript
@app.get('/summary/')
def rishavGemini(code : str = None,count : str =300):
    transcript=""
    url = "https://youtube-transcriptor.p.rapidapi.com/transcript"
    headers = {
    # "X-RapidAPI-Key": "05f93faddamsh06e8d213053c0f4p13558bjsne63c2384e3ca",
    "X-RapidAPI-Key":os.getenv("X_RAPID_API_KEY"),
    "X-RapidAPI-Host": os.getenv("X_RAPID_API_HOST")
    }
    transcript=""
    code=url_to_code(code)
    if(code=="blank"):
        return {"message":"Please enter correct URL "}
    querystring = {"video_id":code}
    response = requests.get(url, headers=headers, params=querystring)
    print(response.json())
    try:
        for content in response.json()[0]['transcription']:
            transcript = transcript + str(content['subtitle'])+" "
    except KeyError as Ie:
        print(f"Index error {Ie}")
        return {"message":"No Script available for this video"}
    
    if(int(response.json()[0]['lengthInSeconds'])>5400):
        return {"message":"Please provide the video's code length less than 90 minutes."}

    if(transcript==""):
        return {"message":"sorry the subtitles are not available for this video"}
    
    # genai.configure(api_key="AIzaSyDfBUXvWleeus9K2s0zCXHqsQMnQgdmAak")
    # response = model.generate_content("Prepare a report or article over the script of a video in english:-  "+transcript)
    # response = model.generate_content("Briefly describe the youtube video with video id  "+str(code)+" ")
    # print(response._chunks)
    # print(response.text)
    # title=[0]['title']
    completion = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        {"role": "system", "content": f'''You are a technical blog and post writer . You will be given a script . You have to Create an article over the given Scripts <Title and Description would be provided > in maximum {count} words <NOTE> * Do not disclose you are a LLM , write the article as a human(Technical writer)* include code snippet , formula and diagram if possible  * Give output in such a way that response will be directed feed to a <div> element of a webpage </NOTE> <OUTPUT> (remember to include the ```html) </OUTPUT>'''}, 
        {"role": "user", "content": f''' <Srcipt> {transcript} </Scripts>''' }  
    ]
    )
    # print(f"summary response {response}")
    # print(response.prompt_feedback)
    return {"message":str(completion.choices[0].message.content).split('```html')[1][:-3]}

@app.get('/askme/')
def askme(code : str = None , ques :str =None):
    transcript=""
    url = "https://youtube-transcriptor.p.rapidapi.com/transcript"
    headers = {
    # "X-RapidAPI-Key": "05f93faddamsh06e8d213053c0f4p13558bjsne63c2384e3ca",
    "X-RapidAPI-Key":os.getenv("X_RAPID_API_KEY"),
    "X-RapidAPI-Host": os.getenv("X_RAPID_API_HOST")
    }
    transcript=""
    code=url_to_code(code)
    if(code=="blank"):
        return {"message":"Please enter correct URL "}
    querystring = {"video_id":code}
    response = requests.get(url, headers=headers, params=querystring)
    try:
        for content in response.json()[0]['transcription']:
            transcript = transcript + str(content['subtitle'])+" "
    except KeyError as Ie:
        print(f"Index error {Ie}")
        return {"message":"No Script available for this video"}
    
    if(int(response.json()[0]['lengthInSeconds'])>5400):
        return {"message":"Please provide the video's code length less than 90 minutes."}
    

    # genai.configure(api_key="AIzaSyDfBUXvWleeus9K2s0zCXHqsQMnQgdmAak")

    # response= model.generate_content("Answer the question "+ques+" from the context "+transcript+" of the video in English:- ")
    completion = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        {"role": "system", "content": f"You are a Question Answering chatbot (name = Chitti) , who reply to questions of the user from the given context only <NOTE> * Do not disclose you are a LLM , write the article as a human(Technical writer) * Give output in such a way that response will be directed to a <div> element of a webpage </NOTE> <OUTPUT> (remember to include the ```html) </OUTPUT>" }, 
        {"role": "user", "content": f''' <Srcipt> {transcript} </Scripts> <Question> {ques} </Question>''' }  
    ]
    )
    # print(response.text)
    return {"message":str(completion.choices[0].message.content).split('```html')[1][:-3]}


@app.get('/question/')
def rishavGemini(q : str='10',code : str = None):
    transcript=""
    url = "https://youtube-transcriptor.p.rapidapi.com/transcript"



    headers = {
    # "X-RapidAPI-Key": "05f93faddamsh06e8d213053c0f4p13558bjsne63c2384e3ca",
    "X-RapidAPI-Key":os.getenv("X_RAPID_API_KEY"),
    "X-RapidAPI-Host": os.getenv("X_RAPID_API_HOST")
    }
    transcript=""
    code=url_to_code(code)
    if(code=="blank"):
        return {"message":"Please enter correct URL "}
    querystring = {"video_id":code}
    response = requests.get(url, headers=headers, params=querystring)
    try:
        for content in response.json()[0]['transcription']:
            transcript = transcript + str(content['subtitle'])+" "
    except KeyError as Ie:
        print(f"Index error {Ie}")
        return {"message":"No Script available for this video"}
    
    if(int(response.json()[0]['lengthInSeconds'])>5400):
        return {"message":"Please provide the video's code length less than 90 minutes."}

    # print(transcript)
    if(transcript==""):
        return {"message":"sorry the subtitles are not available for this video"}
    
    completion = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        
        {"role": "user", "content": f"Create {str(q)} questions along with their answers from the following scripts only <Scripts> {transcript} </Scripts> <Note> * Only inclue those question for which answers are there ?  * Do not disclose you are a LLM  * inclue proper numbering and indexing\
        * Give output in such a way that response will be directed to a <div> element of a webpage . </NOTE> <OUTPUT> (remember to include the ```html) </OUTPUT>" }  ,
    ],
    )

    
    return {"message":str(completion.choices[0].message.content).split('```html')[1][:-3]}
# start: List[int] = Query(...),  # q... means required
    # end: List[int] = Query(...),
@app.get('/social_post/')
def createPostDemo(code : str , platform : str ,start_h : str ,start_m : str,start_s :str,end_h :str,end_m:str,end_s:str ,word : str='100'):
    script=get_scripts_by_timing(code , [start_h,start_m,start_s] , [end_h,end_m,end_s])
    completion = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        {"role": "system", "content": f"You are a technical blog and post writer . You will be given a script .\
        You have to Create a {platform} post over the given Scripts <Title and Description would be provided > in only {word} words\
        NOTE:- Do not disclose you are a LLM or source of your script, write the article as a human(Technical writer) . This would be directly posted to the \
        {platform} . Take your time while creating your post , as this will be for knowledge sharing and creating new connection .\
        * Give output in such a way that response will be directed to a <div> element of a webpage . </NOTE> <OUTPUT> (remember to include the ```html) </OUTPUT>"}, 
        {"role": "user", "content": f''' <Title> {script['Title']} </Title> <Description> {script['Description']} </Description> <Srcipt> {script['Scripts']} </Scripts>''' }  
    ]
    )
    # print(messages)
    return {"message":str(completion.choices[0].message.content).split('```html')[1][:-3]}
   
