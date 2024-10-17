# CustomLLM_Plan_And_Execute_Architecture

# Project: Task Planner and Executor using LLM
Overview
- This Python script implements a task planner and executor system using a large language model (LLM) powered by Groq. The system processes user input, generates a sequence of actions (plan) using predefined functions, and executes them with the appropriate parameters.

# Features
- Dynamic Function Mapping: The script maps function names to specific parameter models and generates corresponding prompts.
- Task Planning with LLM: It uses an LLM (Llama3-8b-8192) to create a step-by-step plan based on user input.
- Function Execution: Executes functions based on the generated plan and validates parameters before execution.
- Functionality: Supports createEvent, deleteEvent, and sendEmail actions, with placeholder prompts for parameter filling.
- Error Handling: Captures and logs execution errors, ensuring robustness in function execution.

# Input
The program accepts natural language tasks from the user and generates a corresponding plan using a few predefined functions:

- createEvent: Adds an event to the user's calendar.
- deleteEvent: Removes an event from the user's calendar.
- sendEmail: Sends an email to a recipient with a provided message.

Example Input:
"Create a meeting from 10-11am on 10/20/2024"

Example Output:
Plan(steps=[Step(function_name='createEvent', context='Event name: meeting, start time: 10am, end_time: 11am, data: 2024-10-20')])

{
  "results": [
    {
      "event_name": "meeting",
      "start_time": "10am",
      "end_time": "11am",
      "date": "2024-10-20"
    },
    ...
  ]
}

Processing Step: createEvent()

Event Name: Meeting, 
Start Time: 10am, 
End Time: 11am, 
Date: 2024-10-20

# Installation
Clone the repository.
Install the required dependencies using pip:
pip install pydantic groq

Set your Groq API key in your environment:
export GROQ_API_KEY="your_api_key_here"
