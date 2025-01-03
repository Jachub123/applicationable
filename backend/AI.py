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

        # Call OpenAI Chat API
        response = openai.chat.completions.create( model    = AI_model,
                                                   messages = task,
                                                   temperature = 0.5,
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
    session_defaults = {"speaker": "General", "history": [], "job_title": "Unknown", "interview_phase": "introduction"}
    #session = {**session_defaults, **session}  # Ensure all keys are present with defaults

    speaker = session['speaker']
    history = session['history']
    job_title = session['job_title']
    interview_phase = session['interview_phase']
    
    print("preparing taks for interview_phase", interview_phase)

    system_message = {
        'role': 'system',
        'content': (
            "You are a highly professional and skilled member of a job assessment panel, "
            "evaluating a candidate's suitability for the role of {}. The panel comprises experts from various domains, "
            "including HR (focused on interpersonal and organizational skills), management (focused on leadership and strategy), "
            "and technical specialists (focused on role-specific expertise). Ensure the interview is structured, rigorous, and valuable for both the panel and the candidate."
        ).format(job_title)
    }


    phase_instructions = {
        "introduction": (
            "Set a positive tone for the interview. Start with a brief introduction of yourself and your role on the panel. \
             Provide an overview of the interview structure to set expectations, and invite the candidate to share their \
             professional background, key accomplishments, and motivation for pursuing this role."

        ),
        "question": (
            "Build on the candidate's previous responses by asking follow-up questions or seeking clarification. \
             Ensure your engagement reflects your panel role. \
             For example: As an HR representative, you might delve deeper into the candidate’s approach to teamwork. \
             As a manager, you could explore their decision-making processes further. \
             As a technical expert, you might ask for more details on the methods or tools they used in their technical examples."
        ),
        "discussion": (
            "Build on the candidate's previous responses by asking follow-up questions or seeking clarification. \
             Ensure your engagement reflects your panel role.\
             For example: As an HR representative, you might delve deeper into the candidate’s approach to teamwork. \
             As a manager, you could explore their decision-making processes further. \
             As an expert, you might ask for more details on the methods or tools they used in their daily challenges."
        ),
        "evaluation": (
            "Critically assess the candidate's performance across all aspects of the interview. \
             Consider their domain-specific expertise, communication skills, adaptability, and alignment with the role's requirements. \
             Provide a fair rating on a scale of 1-10. Justify your score with specific observations and examples from the interview, \
             and make a recommendation on their suitability for the role."
        ),
        "feedback": (
            "Conclude the interview with a constructive summary of the candidate’s performance. Highlight their key strengths \
             and acknowledge areas where improvement is needed. \
             Ensure the feedback is actionable and provides value to the candidate for their personal and professional development. \
             Present the panel's collective decision on their suitability for the role and explain the rationale behind it. \
             Finally offer the candidate a chance for one more question regarding this evaluation."
        ),
        "open_questions": (
            "Engage with the candidate regarding any questions they may have about their evaluation or the feedback provided. \
             Ensure your responses are clear, respectful, and constructive. \
             Focus on providing clarity, addressing concerns, and reinforcing actionable takeaways that the candidate can use to grow professionally. \
             For example: If the candidate asks for specifics on how they could improve, share detailed insights or examples that align with their role aspirations."
        ),
        "closing":  
            "Thank the candidate for their time and participation in the interview. \
            Reiterate the next steps in the selection process and provide a timeline for when they can expect a decision.\
            Conclude with a professional and encouraging note, regardless of the outcome."

    }

    response_formats = {
        "introduction": {"speaker": "your role", "interview_phase": "introduction", "message": "your message"},
        "question": {"speaker": "your role", "interview_phase": "question", "message": "your question"},
        "discussion": {"speaker": "your role", "interview_phase": "discussion", "message": "your message"},
        "evaluation": {"speaker": "your role", "evaluation": "your evaluation", "recommendation": "your recommendation"},
        "feedback": {"speaker": "Panel as a whole", "interview_phase": "feedback", "message": "your summary"},
        "open_questions": {"speaker": "Panel as a whole", "interview_phase": "open_questions", "message": "your answers"},
        "closing": {"speaker": "Panel as a whole", "interview_phase": "closing", "message": "your closing of the sesson"},
    }

    user_input = next((message for name, message in reversed(history) if name == "user"), None)

    def build_user_message(phase, additional_instructions=""):
        prior_conversation = "\n".join([f"{name}: {message}" for name, message in history[-5:]])  # Limit to last 5 messages
        additional_context = f" Last candidate input: '{user_input}'." if phase == "discussion" and user_input else ""
        return {
            'role': 'user',
            'content': (
                "You are representing {}. Your task is to {}. Here is the interview history:\n{}\n"
                "Provide your response in this format: {}\n{}"
            ).format(
                speaker,
                additional_instructions,
                prior_conversation,
                response_formats[phase],
                additional_context
            )
        }

    if interview_phase not in phase_instructions:
        raise ValueError(f"Unknown interview phase: {interview_phase}")

    user_message = build_user_message(interview_phase, phase_instructions[interview_phase])

    task.append(system_message)
    task.append(user_message)

    return task

###############################################################################
# moderate panel
def panel_moderation(AI_model, initial=False):
    
    panel_members = ["HR", "Manager", "Specialist"]
    questions_per_member = 1
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
        
        # jetzt noch Zeit für eine Frage 
        session['interview_phase'] = "open_questions"
        
        return
    
    #--------------------------------------------------------------------------
    elif session['interview_phase'] == "open_questions":
        
        session['speaker'] = "Moderator"
        
        # create task and call AI
        task    = define_task()
        content = send_request(task, AI_model)
        antwort = content['message']
        
        # antwort in history speichern
        session['history'].append((session['speaker'], antwort))
        
        # nächste phase festlegen
        session['interview_phase'] = "closing"
        
        return
            
    #--------------------------------------------------------------------------
    elif session['interview_phase'] == "closing":
        
        session['speaker'] = "Moderator"
        
        # create task and call AI
        task    = define_task()
        content = send_request(task, AI_model)
        antwort = content['message']
        
        # antwort in history speichern
        session['history'].append((session['speaker'], antwort))
        
        # nächste phase festlegen
        session['interview_phase'] = "closing"
        
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