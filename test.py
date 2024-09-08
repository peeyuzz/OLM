import google.generativeai as genai
from queue import PriorityQueue
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.environ["API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')



def function_registry():
    return {
        "search_files": lambda params: f"Searching for {params['file_type']} files in {params['location']}",
        "create_zip": lambda params: f"Creating zip file named {params['zip_name']} with {params['file_list']}",
        "send_email": lambda params: f"Sending email to {params['recipient']} with subject '{params['subject']}' and attachment {params['attachment']}",
        "schedule_meeting": lambda params: f"Scheduling meeting for {params['date']} with {params['attendees']}",
        "order_food": lambda params: f"Ordering {params['food_item']} for {params['people_count']} people",
        "create_document": lambda params: f"Creating a {params['doc_type']} document titled '{params['title']}'",
        "set_reminder": lambda params: f"Setting a reminder for {params['date']} about '{params['reminder_text']}'",
        "book_flight": lambda params: f"Booking a flight to {params['destination']} for {params['date']}",
        "translate_text": lambda params: f"Translating '{params['text']}' from {params['source_lang']} to {params['target_lang']}",
        "generate_report": lambda params: f"Generating a {params['report_type']} report for the period {params['start_date']} to {params['end_date']}",
        "backup_data": lambda params: f"Backing up {params['data_type']} data to {params['backup_location']}",
        "install_software": lambda params: f"Installing {params['software_name']} version {params['version']} on {params['system']}",
    }

def function_registry_str():
    return {
        "search_files": "lambda params: f\"Searching for {params['file_type']} files in {params['location']}\"",
        "create_zip": "lambda params: f\"Creating zip file named {params['zip_name']} with {params['file_list']}\"",
        "send_email": "lambda params: f\"Sending email to {params['recipient']} with subject '{params['subject']}' and attachment {params['attachment']}\"",
        "schedule_meeting": "lambda params: f\"Scheduling meeting for {params['date']} with {params['attendees']}\"",
        "order_food": "lambda params: f\"Ordering {params['food_item']} for {params['people_count']} people\"",
        "create_document": "lambda params: f\"Creating a {params['doc_type']} document titled '{params['title']}'\"",
        "set_reminder": "lambda params: f\"Setting a reminder for {params['date']} about '{params['reminder_text']}'\"",
        "book_flight": "lambda params: f\"Booking a flight to {params['destination']} for {params['date']}\"",
        "translate_text": "lambda params: f\"Translating '{params['text']}' from {params['source_lang']} to {params['target_lang']}\"",
        "generate_report": "lambda params: f\"Generating a {params['report_type']} report for the period {params['start_date']} to {params['end_date']}\"",
        "backup_data": "lambda params: f\"Backing up {params['data_type']} data to {params['backup_location']}\"",
        "install_software": "lambda params: f\"Installing {params['software_name']} version {params['version']} on {params['system']}\"",
    }

function_dependencies = {
    "search_files": [],
    "create_zip": ["search_files"],
    "send_email": [],
    "schedule_meeting": [],
    "order_food": [],
    "create_document": [],
    "set_reminder": [],
    "book_flight": [],
    "translate_text": [],
    "generate_report": ["search_files"],
    "backup_data": ["search_files"],
    "install_software": [],
}

def gemini_query(prompt):
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
        candidate_count=1,
        temperature=0.5,
    ))
    return response.text

def identify_independent_tasks(user_task):
    prompt = f"""Given the user task: "{user_task}"
    Identify independent subtasks that can be executed in parallel from the list below:
    <FUNCTIONS>{function_registry_str()}</FUNCTIONS> 
    Output should be a Python list of strings, each representing a subtask."""
    
    response = gemini_query(prompt)
    return eval(response)  

# def a_star_search(start, goal, dependencies):
#     frontier = PriorityQueue()
#     frontier.put((0, start))
#     came_from = {start: None}
#     cost_so_far = {start: 0}
    
#     while not frontier.empty():
#         current = frontier.get()[1]
        
#         if current == goal:
#             break
        
#         for next in function_registry().keys():
#             if current in dependencies.get(next, []):
#                 new_cost = cost_so_far[current] + 1
#                 if next not in cost_so_far or new_cost < cost_so_far[next]:
#                     cost_so_far[next] = new_cost
#                     priority = new_cost + 1 
#                     frontier.put((priority, next))
#                     came_from[next] = current
    
#     path = []
#     current = goal
#     while current != start:
#         path.append(current)
#         current = came_from[current]
#     path.append(start)
#     path.reverse()
#     return path

def a_star_search(start, goal, dependencies):
    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    for func in function_registry().keys():
        if not dependencies.get(func):  
            frontier.put((0, func))
            came_from[func] = start  # Directly reachable from start
            cost_so_far[func] = 0

    while not frontier.empty():
        current = frontier.get()[1]

        if current == goal:
            break

        for next in function_registry().keys():
            if current in dependencies.get(next, []):
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + 1  # Simple heuristic
                    frontier.put((priority, next))
                    came_from[next] = current

    if goal not in came_from:
        raise ValueError(f"Goal '{goal}' not reachable from '{start}' with the given dependencies.")

    path = []
    current = goal
    while current is not None: 
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path


import re
def populate_parameters(function_name, task, previous_output, user_prompt):
    print(function_registry_str()[function_name])
    prompt = f"""For the function "{function_name}" and the task "{task} and user prompt {user_prompt}",
    populate the parameters based on the task description and the output of the previous function (if any): {previous_output}.
    Return the result as a Python dictionary wrapped in a string based on: {function_registry_str()[function_name]}
    the output must be a python dictionary, where the key is the name of the parameter and value is the value the parameter must take based on user prompt, current task and the function to be executed"""
    
    response = gemini_query(prompt)
    # print(response)
    cleansed_response = re.sub(r"```(python)?\n", "", response).strip("`")
    print(cleansed_response)
    return eval(cleansed_response)  

def main():
    user_task = input("Enter your task: ")
    independent_tasks = identify_independent_tasks(user_task)
    
    print(f"Identified independent tasks: {independent_tasks}")
    
    for task in independent_tasks:
        print(f"\nProcessing task: {task}")
        start = "start"
        goal = gemini_query(f"What is the final function needed to complete this task: {task}? Respond with just the function name. The only available functions are {function_registry()}")
        
        path = a_star_search(start, goal, function_dependencies)
        print(f"Path found: {path}")
        
        previous_output = None
        for function in path[1:]:  # Skip 'start'
            params = populate_parameters(function, task, previous_output, user_task)
            print(f"Executing {function} with parameters: {params}")
            previous_output = function_registry()[function](params)
            print(f"Output: {previous_output}")

if __name__ == "__main__":
    main()