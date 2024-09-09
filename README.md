# OLM
- An operating system built on functions (AI/machine first) instead of apps and gui (human first) with an LLM at its core
- These functions are responsible for different tasks, imagine google search as calling search_google(query) instead of opening the browser going to google.com and then searching
- The user can delegate a task in natural language/image/audio and the OS must identify the function most suitable for completing the task
- In traditional OS ROM is used to store permanent data for booting, hardware management etc. in our case the ROM will all the functions with their descriptions
- RAM in our new OS will be the context window of the LLM
- When a task is assigned the LLM will be passed the list of all available functions and the task, and has to pick a goal function.
- In case the use query has multiple independent tasks (order pizza and book flight) the LLM needs to identify these so they can be processed in parallel
- Now we need to find a way to execute this function(s)
- Since functions have prerequisites (like to search something you need to be connected to the internet) all the functions will be stored in the form of a directed graph
- We will A* search (we’ll have to train a model to predict the heuristic of each function on the basis of query) to find the optimal path to thi function. For example to order pizza:
(if there is a direct function to order pizza) order_pizza(number_of_pizzas, type, address) will be called
(if there is no direct function) open_browser() → search_website(url) → web_crawler() will be the path, where web_crawler can be a general ai agent for websites
-Once we get the path to the goal function we need to populate their parameters, so we again pass this path to the LLM, which based on the user’s query calls each function in the path with necessary arguments and output of previous function in the path
- One the goal function is executed the process stops
