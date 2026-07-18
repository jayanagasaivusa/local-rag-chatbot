import os
import pandas as pd
from pathlib import Path
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate

def query_excel_file(file_path: str, user_question: str) -> dict:
    try:
        df = pd.read_excel(file_path)
        df.columns = [c.strip() for c in df.columns]
        columns = ", ".join(df.columns.tolist())
        
        from config import OLLAMA_BASE_URL, OLLAMA_LLM_MODEL
        llm = ChatOllama(model=OLLAMA_LLM_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.0)
        
        # STRICT PROMPT: Forces assignment to 'result'
        prompt = ChatPromptTemplate.from_template(
            f"You are a Python Data Analyst. The dataframe 'df' has columns: [{columns}].\n"
            "Write valid Python code to answer: {question}.\n"
            "CRITICAL: You MUST perform the calculation and assign the final answer to a variable named 'result'.\n"
            "Example: result = df['Profit'].sum()\n"
            "Do not include markdown, do not include comments, only output the python code."
        )
        
        chain = prompt | llm
        response = chain.invoke({"question": user_question})
        code = response.content.strip().replace("```python", "").replace("```", "")
        
        # DEBUG: Print the generated code to your terminal so you can see if 'result' is there
        print(f"DEBUG: Generated Code: {code}")
        
        local_vars = {"df": df, "result": None}
        exec(code, {}, local_vars)
        final_result = local_vars.get("result")
        
        # If result is still None, grab the last variable defined in local_vars as a fallback
        if final_result is None:
             final_result = list(local_vars.values())[-1]

        # Formatting
        if isinstance(final_result, (int, float)):
            formatted_response = f"${final_result:,.2f}"
        else:
            formatted_response = str(final_result)
            
        return {"response": formatted_response, "sources": [Path(file_path).name]}
            
    except Exception as e:
        return {"response": f"Calculation Error: {str(e)}", "sources": [Path(file_path).name]}