from flask import session
import random
import os
import json

###############################################################################
# define LLM
def send_request(task, AI_model="llama3.2"):
    
    print("sending request to", AI_model)

    #----------------------------------------------------------------------------------
    # chatgpt
    if "gpt" in AI_model.lower():
        
        import openai
        os.environ["dein openai key"] = "....."

        # Call OpenAI Chat API
        response = openai.chat.completions.create( model    = AI_model,
                                                   messages = task,
                                                   temperature = 0.5
                                                    )

        # print(response)
        content = response.choices[0].message.content
        
        #print("content =", content)
        #print(type(content))
        
        # meist ist der content ein string, in diesem fall in dict wandeln
        if isinstance(content, str):
            try:
                # Parse content string into a dictionary
                # Replace single quotes with double quotes for valid JSON
                valid_json_content = content.replace("'", "\"")
                # Parse the string into a dictionary
                content_dict = json.loads(valid_json_content)
                #print("Parsed content_dict =", content_dict)
                #print("new type:",type(content_dict))

                # Accessing the 'message' key
                if 'message' in content_dict:
                    return content_dict
                else:
                    return {"error": "'message' key not found in content", "content": content_dict}
            except:
                print(f"JSON decoding error: {content}")
                return {"error": "Invalid JSON format", "raw_content": content}

        else:
            print(type(content))
            return content
        
    #----------------------------------------------------------------------------------
    # lokale modelle mit ollama  
    else:

        
        import ollama
        
        debug=False
    
        response = ollama.chat(
            model=AI_model,
            messages=task,
            format="json"
        )
        if debug: print("response"); print(response)
        content = response['message']['content']
        if debug: print("content"); print(content)
        content = json.loads(content.strip().strip("```json").strip())
        
        return content



###############################################################################
# define task
def define_task():
    task = []
    speaker = session['speaker']
    history = session['history']
    job_title = session['job_title']
    interview_phase = session['interview_phase']

    # Common system message
    system_message = {
        'role': 'system',
        'content': (
            "You are a member of a job assessment panel, assessing a candidate's fit for a position as {}. "
            "The panel consists of a Moderator, HR, Manager, and Specialist, each contributing questions and evaluations based on their expertise and responsibility."
        ).format(job_title)
    }

    # Define role-specific instructions
    phase_instructions = {
        "introduction": (
            "Guide the conversation, set expectations, and invite the candidate to introduce themselves. "
            "Example: 'Could you please introduce yourself and tell us a bit about your professional background and why you are interested in this role?'"
        ),
        "question": (
            "Ask targeted questions relevant to the job position based on your expertise. "
            "Wait for the candidate's response before proceeding."
        ),
        "evaluation": (
            "Provide a final evaluation of the candidate's performance throughout the entire interview process. "
            "Rate the candidate on a scale of 1 to 10 based on their responses, professional demeanor, and fit for the position. "
            "Offer a clear recommendation on whether the candidate should be considered for the role, backed by specific reasoning."
        ),
        "feedback": (
            "Summarize the candidate's performance and provide a final decision for hiring or not hiring. "
            "The recommendation must be based on whether the candidate demonstrates skills and competencies that place them in the top 20% of all candidates. "
            "Include a concise statement about the panel's consensus on the candidate's strengths, weaknesses, and overall suitability for the role."
        ),
        "discussion": (
            "Respond thoughtfully to the candidate's last input, incorporating your and the panel's prior assessments."
        )
    }

    # Determine response format
    response_formats = {
        "introduction": {"speaker": "your role", "interview_phase": "introduction",    "message": "your message"},
        "question"    : {"speaker": "your role", "interview_phase": "question",        "message": "your message"},
        "discussion"  : {"speaker": "your role", "interview_phase": "discussion",      "message": "your message"},
        "feedback"    : {"speaker": "Panel as a whole", "interview_phase": "feedback", "message": "your summary"},
        "evaluation"  : {"speaker": "your role", "evaluation": "your evaluation", "recommendation": "your recommendation"},
        
    }

    # Get the last user input for discussion phase
    user_input = next((message for name, message in reversed(history) if name == "user"), None)

    # Helper function to build user message
    def build_user_message(phase, additional_instructions=""):
        return {
            'role': 'user',
            'content': (
                "As a skilled member from the company's {}, you are part of a job assessment panel for the position of {}. "
                "Your task is to {}. "
                "This is the interview so far:\n{}\n"
                "Provide your response using this format: {}"
            ).format(
                speaker,
                job_title,
                additional_instructions,
                history,
                response_formats[phase]
            )
        }

    #----------------------------------------------------------------------------------
    # Validate interview phase
    if interview_phase not in phase_instructions:
        raise ValueError(f"Unknown interview phase: {interview_phase}")

    #----------------------------------------------------------------------------------
    # Build task
    user_message = build_user_message(interview_phase, phase_instructions[interview_phase])
    if interview_phase == "discussion" and user_input:
        user_message['content'] += f" Last candidate input: '{user_input}'."

    task.append(system_message)
    task.append(user_message)

    return task

###############################################################################
# moderate panel
def panel_moderation(AI_model, initial=False):
    
    panel_members = ["HR", "Manager", "Specialist"]
    questions_per_member = 2
    question_loops       = questions_per_member * len(panel_members)

    #--------------------------------------------------------------------------
    if initial:
        
        # define speaker order für die folgende phase "question"
        
        # Generate the random order of speakers
        session['speaker_order'] = generate_random_speaker_order(panel_members, 
                                                          questions_per_member)
        session['speaker_count'] = 0
        #print("speaker_order"); print(session['speaker_order'] )
        
        # generate dummy welcome message without AI
        speaker = "Moderator"
        antwort = "Welcome to our job assessment panel!"
        session['history'].append((speaker, antwort))
        # session['history'] = [("Moderator", "Welcome!")]
        print("antwort AI::\n", antwort)
        
        return    
    
    #--------------------------------------------------------------------------
    if session['interview_phase'] == "introduction":
        
        session['speaker'] = "Moderator"
        
        # create task and call AI
        task    = define_task()
        content = send_request(task, AI_model)
        antwort = content['message']
        
        # antwort in history speichern
        session['history'].append((session['speaker'], antwort))
        
        # nächste phase festlegen
        session['interview_phase'] = "question"
        
        return
        
    #--------------------------------------------------------------------------
    elif session['interview_phase'] == "question":
        
        # define speaker, create task and send task to AI
        session['speaker'] = session['speaker_order'][session['speaker_count']]
        
        if False:
            antwort="what else do you want to tell us?"
        else:
            # create task and call AI
            task    = define_task()
            content = send_request(task, AI_model)
            antwort = content['message']
        
        if not isinstance(antwort, str):
            print("antwort is not a string.")
            print(content)
        
        # antwort in history speichern
        session['history'].append((session['speaker'], antwort))
        
        # nächsten speaker oder nächste phase festlegen
        session['speaker_count'] += 1
        if session['speaker_count'] == question_loops:
            session['interview_phase'] = "evaluation"
            print("session['interview_phase']", session['interview_phase'])
            
        return

    #--------------------------------------------------------------------------
    elif session['interview_phase'] == "evaluation":
        
        # randomly define members for evaluation
        turns_per_member = 1
        session['speaker_order'] = generate_random_speaker_order(panel_members, turns_per_member)
        
        session['evaluation'] = []
        
        # der Reihe nach alle members nach ihrer Bewertung fragen
        for speaker in session['speaker_order']:
            print(" - ", speaker, "bewerted das Interview")
            task    = define_task()
            content = send_request(task, AI_model)
            session['evaluation'].append(content)
        
        # create task and call AI
        # print("evaluation from all members:"); print(session['evaluation'])
        
        #-----------------------------------------------------------------------  
        # nächste phase 
        session['interview_phase'] = "feedback"   
        session['speaker'] = "Moderator"
        print(" - ", session['speaker'], "erstellt das Feedback")
            
        # create task and call AI
        task    = define_task()
        content = send_request(task, AI_model)
        antwort = content['message']
        
        # antwort in history speichern
        session['history'].append((session['speaker'], antwort))
        
        return
            

###############################################################################
# helper functions
def generate_random_speaker_order(panel_members, turns_per_member):
    """
    Generate a random order of speakers where each speaker appears a fixed number of times.
    :param panel_members: List of panel member names.
    :param turns_per_member: Number of turns each panel member gets.
    :return: A list of speakers in randomized order.
    """
    # Create a list with each panel member repeated `turns_per_member` times
    all_turns = panel_members * turns_per_member

    # Shuffle the list to randomize the order
    random.shuffle(all_turns)
    
    return all_turns