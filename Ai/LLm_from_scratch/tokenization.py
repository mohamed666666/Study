import os
import urllib.request
import re

def download_text_file():
    """
    Downloads the text file if it doesn't exist locally.
    
    Returns:
        str: Path to the downloaded file
    """
    file_path = "the-verdict.txt"
    if not os.path.exists(file_path):
        url = ("https://raw.githubusercontent.com/rasbt/"
               "LLMs-from-scratch/main/ch02/01_main-chapter-code/"
               "the-verdict.txt")
        try:
            urllib.request.urlretrieve(url, file_path)
            print(f"Downloaded {file_path}")
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None
    return file_path

def simple_tokenize(text):
    """
    Simple tokenization by splitting on whitespace and punctuation.
    
    Args:
        text (str): Input text to tokenize
        
    Returns:
        list: List of tokens
    """
    # Convert to lowercase and split on whitespace and punctuation
    tokens =  re.split(r'([,.:;?_!"()\']|--|\s)', text)
    return tokens

def load_and_tokenize(file_path):
    """
    Loads text from file and performs tokenization.
    
    Args:
        file_path (str): Path to the text file
        
    Returns:
        tuple: (original_text, tokens)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        tokens = simple_tokenize(text)
        return text, tokens
    except Exception as e:
        print(f"Error reading file: {e}")
        return None, None



print(simple_tokenize("Hello, world!"))











