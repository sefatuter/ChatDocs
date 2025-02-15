import ollama
import psycopg2
import logging
from typing import List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgreSQLAssistant:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="pgllm",
            user="postgres",
            password="psql1234",
            host="localhost"
        )
    
    def hybrid_search(self, query: str, top_n: int = 5) -> List[Tuple]:
        """Perform hybrid vector + full-text search"""
        try:
            # Get embedding as a list of floats
            embedding = ollama.embeddings(
                model="bge-m3:latest",
                prompt=query
            )['embedding']

            # Convert list to a PostgreSQL vector format
            embedding_str = "[" + ",".join(map(str, embedding)) + "]"

            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        heading,
                        content,
                        (0.5 * (1 - (embedding <=> %s::vector))) + 
                        (0.5 * COALESCE(ts_rank_cd(search_tsv, plainto_tsquery('english', %s)), 0)) 
                        AS relevance
                    FROM structured_documents
                    ORDER BY relevance DESC
                    LIMIT %s
                """, (embedding_str, query, top_n))

                results = cur.fetchall()
                return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            self.conn.rollback()
            return []


    def generate_response(self, query: str, results: List[Tuple]) -> str:
        """Generate AI-powered response with context"""
        context = "\n\n".join(
            f"Document {i+1}: {row[1]}"
            for i, row in enumerate(results)
        )
        print("=====================================================CONTEXT=====================================================")
        print(context)
        print()        
        prompt = f"""
            You are a PostgreSQL expert assistant. Use this documentation context:
            {context}

            User query: {query}

            Provide a detailed answer with:
            1. Concise explanation
            2. Version-specific syntax if needed
            3. Example SQL snippet
            4. Best practice recommendations
            5. Related optimization tips

            Format response in Markdown.
            """
        
        # prompt = f"""
        #     You are a PostgreSQL expert assistant. Use this documentation context:
        #     {context}

        #     User query: {query}

        #     Provide a detailed answer with the following structured format:
        #     1. **Concise Explanation**: Provide a clear and succinct explanation of the topic.
        #     2. **Version-Specific Syntax**: If applicable, mention the PostgreSQL version-specific syntax or features.
        #     3. **Example SQL Snippet**: Include an example SQL query or command that demonstrates the concept.
        #     4. **Best Practice Recommendations**: Suggest best practices related to the topic.
        #     5. **Related Optimization Tips**: Offer tips or strategies for optimizing performance related to this topic.

        #     Ensure that the response is well-organized in **Markdown** format, using proper headings, bullet points, and code blocks for clarity.
        # """
        
        try:
            response = ollama.generate(
                model="llama3:instruct",
                prompt=prompt,
                options={"temperature": 0.3, "num_ctx": 4096}
            )
            return response.get('response', "No response generated.")
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return "Error generating response"

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()

if __name__ == "__main__":
    assistant = PostgreSQLAssistant()
    
    try:
        query = "Can I create whole table index in partioned tables?" # Enter Query
        print(f"\nSearching for: {query}")
        
        results = assistant.hybrid_search(query)
        
        if results:
            print(f"\nFound {len(results)} relevant documents")
            response = assistant.generate_response(query, results)
            print("\n📘 Generated Response:")
            print(response)
        else:
            print("No results found.")
            
    finally:
        assistant.close()