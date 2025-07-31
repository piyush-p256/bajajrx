# import time
# import requests
# import os
# from typing import List, Dict
# from functools import wraps

# def retry_with_backoff(max_retries=5, backoff_factor=2):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             retries = 0
#             delay = 1
#             while retries < max_retries:
#                 try:
#                     return func(*args, **kwargs)
#                 except requests.exceptions.RequestException as e:
#                     if e.response is not None and e.response.status_code == 429:
#                         print(f"[!] Rate limited. Retrying in {delay}s...")
#                         time.sleep(delay)
#                         delay *= backoff_factor
#                         retries += 1
#                     else:
#                         raise e
#             raise Exception(f"Failed after {max_retries} retries.")
#         return wrapper
#     return decorator

# # GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
# # GROQ_MODEL = "llama3-70b-8192"

# GROQ_API_URL = "https://api.together.xyz/v1/chat/completions"
# GROQ_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"


# def build_prompt(context: List[Dict], question: str) -> str:
#     context_text = "\n\n".join([
#         f"[Page {chunk['metadata'].get('page_number', '?')}] {chunk['text']}" for chunk in context
#     ])
#     prompt = f"""
# You are an expert assistant. Use ONLY the provided context to answer the question.
# - Reference the relevant clause or section (with page number if available).
# - Provide a clear, concise answer and a brief rationale.
# - If the answer is not in the context, say \"Not found in provided document.\"

# Context:
# {context_text}

# Question:
# {question}

# Answer (with clause reference and rationale):
# """
#     return prompt.strip()


# def call_groq_llm(prompt: str, model: str = GROQ_MODEL, temperature: float = 0) -> str:
#     api_key = os.getenv("GROQ_API_KEY")
#     if not api_key:
#         raise RuntimeError("GROQ_API_KEY environment variable not set.")
#     headers = {
#         "Authorization": f"Bearer {api_key}",
#         "Content-Type": "application/json"
#     }
#     data = {
#         "model": model,
#         "messages": [{"role": "user", "content": prompt}],
#         "temperature": temperature
#     }
#     response = requests.post(GROQ_API_URL, headers=headers, json=data)
#     response.raise_for_status()
#     return response.json()["choices"][0]["message"]["content"]


# def generate_llm_answers_groq(questions: List[str], contexts: List[List[Dict]], model: str = GROQ_MODEL) -> List[Dict]:
#     """
#     For each question and its context (list of chunks), generate an answer using the Groq LLM.
#     Return a list of dicts: { 'question': ..., 'answer': ... }
#     """
#     results = []
#     for question, context_chunks in zip(questions, contexts):
#         prompt = build_prompt(context_chunks, question)
#         try:
#             answer = call_groq_llm(prompt, model=model)
#         except Exception as e:
#             answer = f"Error: {str(e)}"
#         results.append({
#             'question': question,
#             'answer': answer
#         })
#     return results 

import os
from typing import List, Dict
from together import Together


client = Together(api_key=os.getenv("TOGETHER_API_KEY"))


def build_prompt(context: List[Dict], question: str) -> str:
    context_text = "\n\n".join([
        f"[Page {chunk['metadata'].get('page_number', '?')}] {chunk['text']}" for chunk in context
    ])
    prompt = f"""
You are an expert assistant. Use ONLY the provided context to answer the question.
- Provide a clear, concise answer and straightforward short answer within 10 words.
- If the answer is not in the context, say \"Not found in provided document.\"

Context:
{context_text}

Question:
{question}

Answer (with clause reference and rationale):
"""
    return prompt.strip()


def call_together_llm(prompt: str, model: str = "Qwen/Qwen3-235B-A22B-Thinking-2507", temperature: float = 0) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response.choices[0].message.content


def generate_llm_answers_together(questions: List[str], contexts: List[List[Dict]], model: str = "Qwen/Qwen3-235B-A22B-Thinking-2507") -> List[Dict]:
    results = []
    for question, context_chunks in zip(questions, contexts):
        prompt = build_prompt(context_chunks, question)
        try:
            print(f"Generating answer for question: {question}")
            print(f"Using model: {model}")
            answer = call_together_llm(prompt, model=model)
        except Exception as e:
            answer = f"Error: {str(e)}"
        results.append({
            'question': question,
            'answer': answer
        })
    return results
