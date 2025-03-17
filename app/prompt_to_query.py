from langchain_community.utilities import SQLDatabase
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate
import re
from typing import List, Optional
import os
from config import DEFAULT_DB_CONFIG, NVIDIA_API_KEY

db = None

def connect_db(db_name):
    global db
    psql_uri = f"postgresql://{DEFAULT_DB_CONFIG['user']}:{DEFAULT_DB_CONFIG['password']}@{DEFAULT_DB_CONFIG['host']}:{DEFAULT_DB_CONFIG['port']}/{db_name}"
    db = SQLDatabase.from_uri(psql_uri)
    return db

def get_database_schema():
    if not db:
        raise ConnectionError("Please connect to the database first.")
    return db.get_table_info()

def get_database_tables():
    if not db:
        raise ConnectionError("Please connect to the database first.")
    return db.get_table_names()

template = """Below is the schema of my PostgreSQL database. Carefully analyze the schema, including tables and column names, to generate the most accurate SQL query for the given question.

Schema:
{schema}


Only use tables and columns that exist in the provided schema. If the required table or column is missing, return: "The requested table or column does not exist in the schema." Do not make assumptions or create fictional table names. Only provide the SQL query, without explanations or comments.

here are the tables use these: {tables}

Examples:

Question: Retrieve the total number of records in a specific table.
SQL Query: ```sql
SELECT COUNT(*) FROM table_name;
```

Question: Retrieve specific columns from a table.
SQL Query: ```sql
SELECT column1, column2 FROM table_name;
```
Question: Perform an aggregate function on a numerical column.
SQL Query: ```sql
SELECT aggregate_function(column_name) FROM table_name;
```

(Can handle multiple tables and generate accurate SQL queries with proper joins, conditions, and aggregations based on the provided schema.)
(please use only provided schema's table and columns)

Your Turn:
Question: {question}
SQL Query (please only provide the valid SQL query and nothing else):

if you made mistake in previous SQL query responses here is the errors (if you don't see any errors ignore this): 

{errors}

based on this errors rewrite SQL query and nothing else. Please only write one SQL query valid and nothing else.
"""

# Natural language explanation prompt
template2 = """Below is the schema of my PostgreSQL database. Carefully analyze the schema, including table and column names, and convert the SQL query result into a detailed and contextual natural language response.

Schema:
{schema}

Instructions:
- The response should be a concise and well-structured explanation of the query result, applicable to any type of database.
- Do not include titles such as "Question," "SQL Query," or "Result." The response should start directly with the explanation in a natural narrative style.
- The response should **start immediately with the explanation** in a narrative style.
- If the result is a count, describe its significance in relation to the dataset, business, or domain.
- If the result involves sums, averages, or percentages, explain its relevance within the dataset, such as financial performance, customer trends, or operational efficiency.
- If the result includes names, identifiers, or categories, emphasize their importance and any patterns they reveal.
- If the query involves relationships between tables, explain the connections between entities and their implications.
- Avoid generic responses; provide meaningful insights tailored to the query's context.
- Ensure the response is relevant to the database type (e.g., a sales database should highlight revenue trends, while a customer database should focus on engagement or retention).
- If the query result is unexpected, highlight possible interpretations or anomalies that may require further investigation.
- If the table or field referenced in the query does not exist in the schema, return: "The requested table or field does not exist in the schema."
- Structure the response in a clear, report-style format that is easy to understand and actionable.

Examples:

Example 1: Identifying the Most Active Customer  
Question: Find the customer with the most movie rentals.  
SQL Query:  
SELECT first_name, last_name, COUNT(rental_id) AS total_rentals  
FROM rental  
JOIN customer ON rental.customer_id = customer.customer_id  
GROUP BY customer.customer_id, first_name, last_name  
ORDER BY total_rentals DESC  
LIMIT 1;  
Result: [('Robert', 'Johnson', 99)]  
Response:  
The table above shows the customer with the highest number of rentals. This customer is Robert Johnson, who has made a total of 99 rentals.  
As one of the most active users of the company, Robert Johnson demonstrates strong engagement with the service.  
Such high activity suggests that he may be a suitable candidate for loyalty programs, special promotions, or personalized offers to enhance customer retention.

Example 2: Analyzing Revenue Trends  
Question: What is the total revenue from all orders?  
SQL Query:  
SELECT SUM(amount) FROM orders;  
Result: [(127500.50,)]  
Response:  
The total recorded revenue from all completed orders in the database is $127,500.50.  
This figure represents the gross earnings generated from transactions, providing a key indicator of the company's financial performance.  
Comparing this number with previous periods can help assess growth trends, profitability, and potential revenue forecasting.

Example 3: Understanding Customer Distribution  
Question: How many customers are from Brazil?  
SQL Query:  
SELECT COUNT(*) FROM customers WHERE country='Brazil';  
Result: [(42,)]  
Response:  
A total of 42 customers in the database are located in Brazil.  
This indicates that a significant portion of the customer base comes from this region, which could be a strategic market for localized marketing campaigns.  
This insight may suggest opportunities for targeted promotions, regional partnerships, or improving customer service operations in Brazil.

Your Turn:  
Question: {question}  
SQL Query: {query}  
Result: {result}  
Response:
"""


def extract_sql_query(response) -> str:
    """Extract SQL query from LLM response"""
    if hasattr(response, 'content'):
        content = response.content
    else:
        content = str(response)
        
    content = re.sub(r"^```sql\s*|\s*```$", "", content.strip(), flags=re.DOTALL)
    
    match = re.search(r"\b(SELECT|INSERT|UPDATE|DELETE)\b\s+.*", content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(0).strip()
    
    return content.strip()

def run_query(query, question: str, db_tables, schema_info: str, max_retries: int = 3) -> tuple:
    """
    Run SQL query with retry mechanism
    Returns (result, query) tuple
    """
    if not db:
        raise ConnectionError("Please connect to the database first.")
    
    errors = []
    current_query = query
    
    # Regenerate aux - if error occurs .
    llm = ChatNVIDIA(
        model="meta/llama-3.1-405b-instruct",
        api_key=NVIDIA_API_KEY,
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024
    )
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm
    
    for attempt in range(max_retries):
        try:
            # Clean and run the query
            cleaned_query = extract_sql_query(current_query)
            print(f"Attempt {attempt+1} - Running query:\n{cleaned_query}")
            result = db.run(cleaned_query)
            
            # Check if result is empty
            if result and result != "None":
                return result, cleaned_query
            else:
                error_msg = "Query executed but returned empty results."
                print(error_msg)
                errors.append(error_msg)
        
        except Exception as e:
            error_message = str(e)
            print(f"Error executing query: {error_message}")
            errors.append(error_message)
        
        if attempt < max_retries - 1:
            print(f"Regenerating query (attempt {attempt+2}/{max_retries})...")
            response = chain.invoke({
                "question": question,
                "schema": schema_info,
                "tables": db_tables,
                "errors": errors
            })
            current_query = extract_sql_query(response)
        
    raise Exception(f"Failed to execute query after {max_retries} attempts. Last errors: {errors}")

def get_database_schema():
    """Get database schema information"""
    if not db:
        raise ConnectionError("Please connect to the database first.")
    return db.get_table_info()

def get_database_tables():
    """Get list of database tables"""
    if not db:
        raise ConnectionError("Please connect to the database first.")
    return db.get_table_names()

def process_natural_language_query(question: str, db_name) -> str:
    """Process a natural language query and return response"""
    if not db:
        connect_db(db_name)
    
    schema_info = get_database_schema()
    db_tables = db.get_table_names()

    sql_llm = ChatNVIDIA(
        model="meta/llama-3.1-405b-instruct",
        api_key=NVIDIA_API_KEY,
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024
    )
    sql_prompt = ChatPromptTemplate.from_template(template)
    sql_chain = sql_prompt | sql_llm
    
    response = sql_chain.invoke({
        "question": question,
        "schema": schema_info,
        "tables": db_tables,
        "errors": []
    })
    print(f"Raw SQL response:\n{response}")
    
    try:
        query = extract_sql_query(response)
        result, final_query = run_query(query, question, db_tables, schema_info)
        
        nl_llm = ChatNVIDIA(
            model="meta/llama-3.1-405b-instruct",
            api_key=NVIDIA_API_KEY,
            temperature=0.3,
            top_p=0.7,
            max_tokens=1024
        )
        nl_prompt = ChatPromptTemplate.from_template(template2)
        nl_chain = nl_prompt | nl_llm
        
        explanation_response = nl_chain.invoke({
            "question": question,
            "schema": schema_info,
            "query": final_query,
            "result": result
        })
        
        explanation = explanation_response.content if hasattr(explanation_response, 'content') else str(explanation_response)
        
        return explanation, final_query
        
    except Exception as e:
        return f"Error processing query: {str(e)}"