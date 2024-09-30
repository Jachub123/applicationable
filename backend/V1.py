# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 11:50:09 2024

im Arbeitsverzeichnis:
    python -m venv Langgraph_env
    Langgraph_env/Scripts/activate
    ?? pip install langchain_openai
    pip install -U ollama
    pip install langchain-openai
    pip install -U langgraph                -U To update installed packages to their latest versions
    pip install -U langchain-community      -U To update installed packages to their latest versions

    in VS Code: Ctrl+Shift+P, darin 
        "python: Select Interpreter"
            darin mit Find suchen nach 
            Langgraph_env/Scripts/python.exe


    Fazit:  langgraph ist eine relative komplexe Steuerung des prozesses,
            m.E. genauso gut durch Python Code dargestellt werden kann. 
            Also wann welche Aktion gestartet wird:
            - jeder Interviewer hat 'total_questions_per_round'  : 3,
            - danach wird eine Bewertung erstellt
            - wenn alle Interviewer durch sind
            - wird die abschließende Entscheidung getroffen

            Gut ist das einfache Handling der history:
                - {"history":history+'\n\n'+answer,"current_answer":answer}
            und das formatieren mit 
                - .format(.....)


@author: koeng
"""

#Importing packages

import os

from typing import Dict, TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain.output_parsers import CommaSeparatedListOutputParser

from langchain_openai import OpenAI

#------------------------------------------------------------------------------------------------------------

api_key = "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"
model   = "gpt-3.5-turbo-instruct"
# geht nicht, da altes interface mit chatcompletionmodel   = "gpt-4-1106-preview"
# geht nicht, da altes interface mit chatcompletion model   = "gpt-3.5-turbo"

Model = "llama3"
Model = "ChatGPT"

if Model == "ChatGPT":
    llm = OpenAI(model_name=model, 
                openai_api_key=api_key)

# llama3 hat ein modul ....complete oder so ähnlich, 
elif Model == "llama3":    # tut so nicht, wie startet man llama3 auf diese Wiese
    import ollama
    llm = ollama.chat(model='llama3')

elif Model == "Phi3":
    llm = OpenAI(model_name = "phi3", 
                 base_url   = "http://127.0.0.1:11434",
                 openai_api_key = "none")


#------------------------------------------------------------------------------------------------------------
#Setting StateGraph variables
#------------------------------------------------------------------------------------------------------------
class GraphState(TypedDict):
    all_history     : Optional[str] = None
    history         : Optional[str] = None
    result          : Optional[str] = None
    final_result    : Optional[str] = None
    total_questions : Optional[int] = None
    interviewer     : Optional[str] = None
    candidate       : Optional[str] = None
    current_question: Optional[str] = None
    current_answer  : Optional[str] = None
    round           : Optional[int] = None
    panel           : Optional[list]= []
    total_rounds    : Optional[int] = None
    total_questions_per_round: Optional[int] = None

workflow = StateGraph(GraphState)

#------------------------------------------------------------------------------------------------------------
#Different Agent prompts used
#------------------------------------------------------------------------------------------------------------
prompt_interviewer = "You're a {}. You need to interview a {}. This is the interview so far:\n{}\n\
Ask your next question and dont repeat your questions.\
Output just the question and no extra text"

prompt_interviewer = "You're a {}. You need to interview a {}. This is the interview so far:\n{}\n\
Tailor your questions to reflect your specific roles and responsibilities within the company, \
ensuring the interview covers a comprehensive range of topics and dont repeat your questions.\
Output just the question and no extra text"

prompt_interviewee = "You're a {}. You've appeared for a job interview.\
Answer the question asked. Output just the answer as paragraph and no extra text. Question:{}"

prompt_result = "Evaluate the performance of the candidate based on the response given for the questions asked\
    give a rating on a scale of 10. Explain the rating in very short paragraph.\nThe interview:\n{}"

prompt_verdict="Given the interview, should we select the candidate?\
    Give output as Yes or No with a reason.\nThe interview:\n{}"

prompt_cleanup = "Remove empty dialogues, repeated sentences and repeate names to convert this input as a conversation.\
                  Output just the Interview and no extra text. \nInterview:\n{}"

#------------------------------------------------------------------------------------------------------------
# Defining nodes for LangGraph
#------------------------------------------------------------------------------------------------------------
def handle_question(state):
    ''' Let the current interviewer agent generate the next 
        question based on the conversation so far (history).'''
    history     = state.get('history', '').strip()                              #  <-- history, role und candidate festlengen
    role        = state.get('interviewer', '').strip()
    candidate   = state.get('candidate', '').strip()                            
    prompt      = prompt_interviewer.format( role, candidate, history)          #  <-- hier wird der prompt an lmm zusammegestellt
    question    = role +":"+ llm(prompt)                                        #  <-- hier generiert lmm die Frage auf Basis des prompts
    if history  == 'Nothing':
        history = ''
    return {"history":history+'\n\n'+question,"current_question":question,"total_questions":state.get('total_questions')+1}

def handle_response(state):
    '''  This generates the answer for the question being asked '''
    history     = state.get('history', '').strip()                              #  <-- history holen
    question    = state.get('current_question', '').strip()                     #  <-- Frage von lmm holen
    candidate   = state.get('candidate', '').strip()                            #  <-- Kandidat diefinieren
    prompt      = prompt_interviewee.format(candidate,question)                 #  <-- hier generiert lmm die Antwort auf Basis des prompts
    answer      = candidate +":"+ llm(prompt)                                   #  <-- hier generiert lmm die Antwort des Kandidaten auf Basis des prompts
    return {"history":history+'\n\n'+answer,"current_answer":answer}

def handle_result(state):
    ''' Based on the entire round, the interviewer gives a feedback 
        and rating for the interviewee'''
    history     = state.get('history', '').strip()                              #  <-- history holen
    interviewer = state.get('interviewer', '').strip()                          #  <-- Interviewer festlegen
    round       = state.get('round')                                            #  <-- Fragen des Interviewers zählen
    panel       = state.get('panel')                                            #  <-- Panel (alle Interviewer holen)
    prompt      = prompt_result.format(history)                                 #  <-- Prompt für die Bewertung des Kandidaten zusammensten mit history
    result      = llm(prompt)                                                   #  <-- Ergebnis der Bewertung holen
    all_history = state.get('all_history', '').strip()
    result      =  " \nInterviewed by {}\n{}".format(interviewer,result)
    print("ROUND {} done by {}".format(round+1,interviewer))
    try:
        next = panel[round+1]                                                   #  <-- nächsten Interviewer festlegen
    except:
        next = ''
    return{"result":state.get('result')+'\n'+result,'history':'Nothing',"all_history":all_history+'\n\n INTERVIEWED BY {} \n'.format(interviewer)+history,\
           'round':round+1,'interviewer':next,'total_questions':0}

def handle_selection(state):
    ''' Based on feedback from all the rounds, decide whether the interviewee 
        should be selected or not'''
    result = state.get('result', '').strip()                                    #  <-- hier wird das bisherige Ergebnis geholt
    prompt = prompt_verdict.format(result)                                      #  <-- prompt erstellen, ob der Kandidat eingestellt werden kann
    result = llm(prompt)                                                        #  <-- hier wird entschieden, ob der Kandidat aeingestellt werden kann
    return{"final_result":result}

#------------------------------------------------------------------------------------------------------------
# Add the above defined nodes into the workflow graph object.
# dies ist der Prozess für eine Frage
#------------------------------------------------------------------------------------------------------------
workflow.add_node("handle_question", handle_question)                           #  <-- hier generiert lmm die Frage 
workflow.add_node("handle_response", handle_response)                           #  <-- hier generiert lmm die Antwort des Kandidaten 
workflow.add_node("handle_result",   handle_result)                             #  <-- hier erstellt llm die Bewertung des Kandidaten
workflow.add_node("handle_selection",handle_selection)                          #  <-- hier wird entschieden, ob der Kandidat eingestellt werden kann

#------------------------------------------------------------------------------------------------------------
# Defining conditional edges
#------------------------------------------------------------------------------------------------------------

def check_conv_length(state):                                                   #  <-- in Abhängigkeit wieviele Fragen der Interviewer bereits gestellt hat, wird definiert, was nach "handle_response" passieren soll
    ''' This helps us to end a specific round once the threshold questions (say 5) 
        have been asked by the interviewer. '''
    return "handle_question" if state.get("total_questions")<state.get("total_questions_per_round") else "handle_result"

def check_rounds(state):
    ''' this helps in ending the interview process given all the rounds are done. '''
    return "handle_question" if state.get("round")<state.get("total_rounds") else "handle_selection"

workflow.add_conditional_edges(
    "handle_response",                                                          #  <-- condition nach "handle_response" 
    check_conv_length,                                                          #  <-- in Abhängigkeit wieviele Fragen der Interviewer bereits gestellt hat, wird definiert, was nach "handle_response" passieren soll
    {
        "handle_question": "handle_question",                                   #  <-- wenn noch nicht alle Fregen gestellt, nächste Frage
        "handle_result": "handle_result"                                        #  <-- wenn alle Fragen gestellt, Bewertung erstellen
    }
)
workflow.add_conditional_edges(
    "handle_result",                                                            #  <-- condition nach "handle_result" 
    check_rounds, 
    {                                                                           #  <-- alle Fragen eines Interviewers abgeschlossen?
        "handle_question": "handle_question",                                   #  <-- wenn nicht, weiterfragen mit nächstem Interviewer
        "handle_selection": "handle_selection"                                  #  <-- doch, Auswahlpanel starten
    }
)
workflow.set_entry_point("handle_question")                                     #  <-- Einstiegspunkt in den Workflow
workflow.add_edge('handle_question', "handle_response")                         #  <-- checks nach ...??????
workflow.add_edge('handle_selection',END)                                       #  <-- letzter Schritt Kandidatenauswahl

#------------------------------------------------------------------------------------------------------------
# Compile the graph object
#------------------------------------------------------------------------------------------------------------
app = workflow.compile()

#------------------------------------------------------------------------------------------------------------
# Determining panel: wer sind die Interviewer
#------------------------------------------------------------------------------------------------------------
interview_role  = 'data scientist'
interview       = "Suggest a interview panel to interview a {}. Suggest just the roles as comma separated list and nothing else. Dont use new line character".format(interview_role)
output_parser   = CommaSeparatedListOutputParser()
classes         = output_parser.parse(llm(interview))
classes         = [ 'Data Scientist', 'Human Resources Manager', 'Works Council', 'Department Manager']
print("classes suggested", classes)

#------------------------------------------------------------------------------------------------------------
# Invoke the graph object & initiate interview
#------------------------------------------------------------------------------------------------------------
conversation = app.invoke({'total_questions'            : 0,
                           'candidate'                  : interview_role,
                           'total_rounds'               : len(classes),
                           'total_questions_per_round'  : 3,
                           'round'                      : 0,
                           'result'                     : '',
                           'all_history'                : '',
                           'interviewer'                : classes[0],
                           'panel'                      : classes,
                           'history'                    : 'Nothing',
                           'round'                      : 0,
                           'all_history'                : ''},
                          {"recursion_limit":1000})

#------------------------------------------------------------------------------------------------------------
# Checkout the final decision
#------------------------------------------------------------------------------------------------------------
print(conversation['final_result'])
print("--------------------------------------------------------")
print(conversation['all_history'])
print("--------------------------------------------------------")
print(conversation['result'])



