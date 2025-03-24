import pandas as pd
import numpy as np
from typing import List, Dict, Any

def chunk_dataframe(df: pd.DataFrame, max_rows: int = 10) -> List[pd.DataFrame]:
    """
    Split dataframe into smaller chunks to respect token limits.
    
    Args:
        df: Input dataframe
        max_rows: Maximum number of rows per chunk
        
    Returns:
        List of dataframe chunks
    """
    return [df[i:i + max_rows] for i in range(0, len(df), max_rows)]

def format_data_for_prompt(df_chunk: pd.DataFrame) -> str:
    """
    Format a chunk of dataframe data into a prompt-friendly string.
    
    Args:
        df_chunk: Chunk of dataframe to format
        
    Returns:
        Formatted string containing relevant information
    """
    formatted_text = "Here are the companies and their rationales:\n\n"
    
    for _, row in df_chunk.iterrows():
        formatted_text += f"Company: {row['short_name']}\n"
        formatted_text += f"Sector: {row['gics_1_sector']}\n"
        formatted_text += f"Rationale: {row['Conf_rationale']}\n"
        formatted_text += f"Revenue Description: {row['Most_aligned_rev_desc']}\n"
        formatted_text += f"Composite Score: {row['Composite_Score']}\n"
        formatted_text += "-" * 50 + "\n"
    
    return formatted_text

def analyze_with_chatgpt(df: pd.DataFrame, question: str, max_rows: int = 10) -> str:
    """
    Analyze dataframe data using ChatGPT while managing token limits.
    
    Args:
        df: Input dataframe
        question: User's question about the data
        max_rows: Maximum number of rows to process at once
        
    Returns:
        ChatGPT's response
    """
    # Split dataframe into chunks
    chunks = chunk_dataframe(df, max_rows)
    
    # Initialize system prompt
    system_prompt = """You are a professional financial analyst. Analyze the provided company data and answer questions about their rationales, sector composition, and overall trends. Be concise but thorough in your analysis."""
    
    # Process each chunk and combine responses
    all_responses = []
    
    for i, chunk in enumerate(chunks):
        chunk_text = format_data_for_prompt(chunk)
        
        # Create messages for ChatGPT
        messages = [
            {"promptRole": "system", "prompt": system_prompt},
            {"promptRole": "user", "prompt": f"Here is chunk {i+1} of {len(chunks)} of company data:\n\n{chunk_text}\n\nQuestion: {question}"}
        ]
        
        # Get ChatGPT response
        response = AI.get_surface_chat_completion(messages)['chatCompletion']['chatCompletionContent']
        all_responses.append(response)
    
    # Combine all responses
    final_response = "\n\n".join(all_responses)
    
    # Get a final summary if there were multiple chunks
    if len(chunks) > 1:
        summary_messages = [
            {"promptRole": "system", "prompt": system_prompt},
            {"promptRole": "user", "prompt": f"Here are the analyses of different chunks of company data:\n\n{final_response}\n\nPlease provide a concise summary of the key findings across all chunks."}
        ]
        final_response = AI.get_surface_chat_completion(summary_messages)['chatCompletion']['chatCompletionContent']
    
    return final_response

def get_sector_summary(df: pd.DataFrame) -> str:
    """
    Get a summary of sector composition and trends.
    
    Args:
        df: Input dataframe
        
    Returns:
        ChatGPT's analysis of sector composition
    """
    question = "Analyze the sector composition of these companies and identify any notable trends or patterns."
    return analyze_with_chatgpt(df, question)

def get_rationale_analysis(df: pd.DataFrame) -> str:
    """
    Analyze the rationales provided for the companies.
    
    Args:
        df: Input dataframe
        
    Returns:
        ChatGPT's analysis of company rationales
    """
    question = "Analyze the rationales provided for these companies. What are the common themes and unique aspects?"
    return analyze_with_chatgpt(df, question) 