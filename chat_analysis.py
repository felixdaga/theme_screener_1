import pandas as pd
import numpy as np
from typing import List, Dict, Any

def chunk_dataframe(df: pd.DataFrame, chunk_size: int = 10) -> List[pd.DataFrame]:
    """
    Split dataframe into smaller chunks to respect token limits.
    
    Args:
        df: Input dataframe
        chunk_size: Number of rows per chunk
        
    Returns:
        List of dataframe chunks
    """
    return [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]

def format_data_for_prompt(df_chunk: pd.DataFrame) -> str:
    """
    Format a chunk of dataframe data into a prompt-friendly string.
    
    Args:
        df_chunk: Chunk of dataframe to format
        
    Returns:
        Formatted string containing relevant information
    """
    formatted_text = "Here are the companies and their details:\n\n"
    
    for _, row in df_chunk.iterrows():
        formatted_text += f"Company: {row['short_name']}\n"
        for col in df_chunk.columns:
            if col != 'short_name':  # Skip short_name as it's already included
                formatted_text += f"{col}: {row[col]}\n"
        formatted_text += "-" * 50 + "\n"
    
    return formatted_text

def analyze_with_chatgpt(df: pd.DataFrame, question: str, chunk_size: int = 10) -> str:
    """
    Analyze dataframe data using ChatGPT while managing token limits.
    
    Args:
        df: Input dataframe
        question: User's question about the data
        chunk_size: Number of rows to process at once
        
    Returns:
        ChatGPT's response
    """
    # Split dataframe into chunks
    chunks = chunk_dataframe(df, chunk_size)
    
    # Initialize system prompt
    system_prompt = """You are a professional financial analyst. Analyze the provided company data and answer questions about their characteristics, composition, and overall trends. Be concise but thorough in your analysis. Focus on providing actionable insights and clear patterns in the data."""
    
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

def get_sector_summary(df: pd.DataFrame, chunk_size: int = 10) -> str:
    """
    Get a summary of sector composition and trends.
    
    Args:
        df: Input dataframe
        chunk_size: Number of rows to process at once
        
    Returns:
        ChatGPT's analysis of sector composition
    """
    question = "Analyze the sector composition of these companies and identify any notable trends or patterns."
    return analyze_with_chatgpt(df, question, chunk_size)

def get_rationale_analysis(df: pd.DataFrame, chunk_size: int = 10) -> str:
    """
    Analyze the rationales provided for the companies.
    
    Args:
        df: Input dataframe
        chunk_size: Number of rows to process at once
        
    Returns:
        ChatGPT's analysis of company rationales
    """
    question = "Analyze the rationales provided for these companies. What are the common themes and unique aspects?"
    return analyze_with_chatgpt(df, question, chunk_size) 