import os

from typing import List, Optional
import json

from pydantic import BaseModel
from groq import Groq

import tools

groq = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

functionDataList = """
    {function_name: "createEvent", description: "Creates an event and places it on the users calender"},
    {function_name: "deleteEvent", description: "Removes an event from the users calender"},
    {function_name: "sendEmail", description: "Sends a given message to a specified person"}
"""

# Data model for LLM to generate
createEvent_ParameterPrompt = "" # Guides the model on how to input parameters
class CreateEvent_Parameters(BaseModel):
    event_name: str
    start_time: str
    end_time: str
    date: str
    
deleteEvent_ParameterPrompt = ""
class DeleteEvent_Parameters(BaseModel):
    event_name: str
    
sendEmail_ParameterPrompt = ""
class SendEmail_Parameters(BaseModel):
    recipient_name: str
    message: str

def findFunctionSchema(functionName: str) -> BaseModel: # Finds a function by name and returns its parameters
    # Mapping function names to their corresponding parameter classes
    function_map = {
        "createEvent": CreateEvent_Parameters,
        "deleteEvent": DeleteEvent_Parameters,
        "sendEmail": SendEmail_Parameters,
    }
    
    # Return the corresponding parameter class, or None if the function name is not found
    return function_map.get(functionName, None)

def findFunctionParameterPrompt(functionName: str) -> BaseModel:
     # Mapping function names to their corresponding parameter classes
    function_map = {
        "createEvent": createEvent_ParameterPrompt,
        "deleteEvent": deleteEvent_ParameterPrompt,
        "sendEmail": sendEmail_ParameterPrompt,
    }
    
    # Return the corresponding parameter class, or None if the function name is not found
    return function_map.get(functionName, None)

class Step(BaseModel):
    function_name: str
    context: str
    
class Plan(BaseModel):
    steps: List[Step]

def Splitter(userInput: str) -> Plan:
    chat_completion = groq.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"""You are a planner that creates steps to completing a given task ONLY using functions. 
                REMEMBER: If you are given a task at ALL unrelated to the functions specific description given below then create a one step plan with function_name: "None", and context: "None" !!!
                Each step in your plan may ONLY pick from one function from the list below and provide relevent context for it to be executed properly.
                {functionDataList} \n"""
                # Pass the json schema to the model. Pretty printing improves results.
                f" The JSON object must use the schema: {json.dumps(Plan.model_json_schema(), indent=2)}",
            },
            {
                "role": "user",
                "content": f"Create a plan for the following task: {userInput}",
            },
        ],
        model="llama3-8b-8192",
        temperature=0,
        # Streaming is not supported in JSON mode
        stream=False,
        # Enable JSON mode by setting the response format
        response_format={"type": "json_object"},
    )
    return Plan.model_validate_json(chat_completion.choices[0].message.content)

#plan = Splitter("Create a meeting named 'my meeting' from 2pm-3pm for next Tuesday and remove my meeting titled 'the other meeting' then lastly send a message to sally telling her I will be late to todays meeting'")
#plan = Splitter("Make an event called coffee then delete an event called coffee then send email to joe telling him i deleted an event called coffee")
#plan = Splitter("Make an event called coffee and make me a coffee") # Tricky task, mixes an action that can be done with an action that cant

userInput = input()
plan = Splitter(userInput)

print(plan)
print("")
print("-----------------")
print("")

prevStepLog = []

def Executor(step: Step) -> BaseModel: # Will only output a summarization of what it accomplished
    
    parameter_model = findFunctionSchema(step.function_name) # Finds the function parameter schema to fill in
    function_parameter_prompt = findFunctionParameterPrompt(step.function_name) # Finds the specific prompt for the function
    
    chat_completion = groq.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"""Your job is to assign or to not assign values to the each parameter in the schema.
                You MUST ONLY assign a value to a parameter if it is explicitly stated.
                If a parameters value is not explicitly stated in the context then you NEED TO ASSIGN IT A BLANK STRING. "" 
                {function_parameter_prompt}"""
                # Pass the json schema to the model. Pretty printing improves results.
                f" The JSON object must use the schema: {json.dumps(parameter_model.model_json_schema(), indent=2)}",
            },
            {
                "role": "user",
                "content": f"Do or do not fill in the schema parameters based on the given context: {step.context}",
            },
        ],
        model="llama3-8b-8192",
        temperature=0,
        # Streaming is not supported in JSON mode
        stream=False,
        # Enable JSON mode by setting the response format
        response_format={"type": "json_object"},
    )
    
    # Executes steps chosen function
    validated_parameter_data = parameter_model.model_validate_json(chat_completion.choices[0].message.content)
    parameter_dict = validated_parameter_data.dict() # Unpack the validated parameters

    try:
        run_function = getattr(tools, step.function_name) # Finds the function in the tools imports by name
        
        try:
            # Execute the function with the validated parameters
            run_function(**parameter_dict)
        except:
            # If the function fails, log the error and return None
            raise Exception("Chosen function was unable to excecute as expected")
            
    except:
        raise Exception("Unable to locate function in tool list")
        
    
    return validated_parameter_data

# Function to process all steps in the plan
def process_plan(plan: Plan):
    results = []
    
    if plan.steps[0].function_name == "None":
        return json.dumps({"results": "No valid steps to execute."}, indent=2)
    
    for step in plan.steps:
        print(f"Processing step: {step.function_name}")
        result = Executor(step)
        results.append(result)
    
    # Return the results as a JSON object
    return json.dumps({"results": [res.json() if isinstance(res, BaseModel) else res for res in results]}, indent=2)

# Example usage of processing the plan
execution_results = process_plan(plan)
print(execution_results)