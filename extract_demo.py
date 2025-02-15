import re
from pdfminer.high_level import extract_pages, extract_text
from typing import List
import json

text_file_path="big_extracted_demo.txt"

structured_data = []

def save_pages(text_file_path):
    text = extract_text("postgresql-14-A4.pdf")
    with open(text_file_path, "w", encoding="utf-8") as file:
        file.write(text)

def split_sentences(text):
    """Splits text into individual sentences while preserving punctuation."""
    if not isinstance(text, str):  # Ensure the input is a string
        text = str(text)
        
    text = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', text)

    sentences = re.split(r'(?<!\d)(?<!\.\.\.)(?<=[.!—])\s+', text)  # Split at punctuation followed by space
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    return sentences

def print_txt(text_file_path):
    
    # Define regex patterns for different heading structures
    patterns = {
        'main_chapter': re.compile(r'^\d+\.\s+[\w\s\-_(),]+$', re.IGNORECASE),
        'sub_chapter': re.compile(r'^\d+\.\d+\.\s+[\w\s\-_(),]+$', re.IGNORECASE),
        'sub_sub_chapter': re.compile(r'^\d+\.\d+\.\d+\.\s+[\w\s\-_(),]+$', re.IGNORECASE),
        'table_of_contents': re.compile(r'^Table of Contents$', re.IGNORECASE),
        'bibliography': re.compile(r'^Bibliography$', re.IGNORECASE),
        'part': re.compile(r'^Part\s+[IVXLCDM]+\.\s+[\w\s\-_(),]+$', re.IGNORECASE),
        'roman_section': re.compile(r'^[IVXLCDM]+\.\s+[\w\s\-_(),]+$', re.IGNORECASE),
        'roman_numbered': re.compile(r'^[IVXLCDM]+\.\d+(\.\d+)*\.\s+[\w\s\-_(),]+$', re.IGNORECASE),
        'lettered_numbered': re.compile(r'^[A-O]\.\s*\d+(\.\d+)*\.\s+[\w\s\-_(),]+$', re.IGNORECASE)
    }

    # Read the text file
    with open(text_file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        
    extracted_data = {}
    current_heading = None

    # Iterate through lines and categorize content under headings
    for line in lines:
        stripped_line = line.strip()
        
        # Check if the line matches any heading pattern
        is_heading = False
        for key, pattern in patterns.items():
            if pattern.match(stripped_line):
                current_heading = stripped_line
                extracted_data[current_heading] = []  # Initialize list for this heading
                is_heading = True
                break
        
        # If it's not a heading, append it under the last found heading
        if not is_heading and current_heading:
            extracted_data[current_heading].append(stripped_line)
    
    # Print extracted headings and their content
    for heading, content in extracted_data.items():
        print(heading)
        print("-" * 50)
        print("\n".join(content))  # Print content under the heading
        print("\n")

def extract_content_under_headings(text_file_path, max_headings):
    # Define regex patterns for different heading structures
    patterns = {
        'chapter': re.compile(r'^\s*Chapter\s+\d+(\.\d+)*\.\s+[\w\s\-_(),/—]+$', re.IGNORECASE),  # Matches "Chapter X." or "Chapter X.Y.Z."
        'sub_chapter': re.compile(r'^\d+\.\d+\.\s+[\w\s\-_(),/]+$', re.IGNORECASE),  # 43.1. Title
        'sub_sub_chapter': re.compile(r'^\d+\.\d+\.\d+\.\s+[\w\s\-_(),/]+$', re.IGNORECASE),  # 43.1.1. Title
        'sub_sub_sub_chapter': re.compile(r'^\d+(\.\d+)+\.\s+[\w\s\-_(),/]+$', re.IGNORECASE),  # 43.1.1.1. or deeper
        'table_of_contents': re.compile(r'^Table of Contents$', re.IGNORECASE),
        'bibliography': re.compile(r'^Bibliography$', re.IGNORECASE),
        'part': re.compile(r'^Part\s+[IVXLCDM]+\.\s+[\w\s\-_(),/]+$', re.IGNORECASE),
        'roman_section': re.compile(r'^[IVXLCDM]+\.\s+[\w\s\-_(),/]+$', re.IGNORECASE),
        'roman_numbered': re.compile(r'^[IVXLCDM]+\.\d+(\.\d+)*\.\s+[\w\s\-_(),/]+$', re.IGNORECASE),
        'lettered_numbered': re.compile(r'^[A-O]\.\s*\d+(\.\d+)*\.\s+[\w\s\-_(),/]+$', re.IGNORECASE)
    }

    # Read the text file
    with open(text_file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    extracted_data = {}
    current_heading = None
    heading_count = 0

    # Iterate through lines and categorize content under headings
    for line in lines:
        stripped_line = line.strip()
        
        # Check if the line matches any heading pattern and is not too long
        is_heading = False
        for key, pattern in patterns.items():
            if pattern.match(stripped_line) and len(stripped_line) <= 50:  # Prevent long lines from being headings
                heading_count += 1
                # if heading_count > max_headings:  # Stop after reaching the limit
                #     break
                
                current_heading = stripped_line
                extracted_data[current_heading] = []  # Initialize list for this heading
                is_heading = True
                break
        
        # If it's not a heading or too long, append it as content
        if (not is_heading or len(stripped_line) > 50) and current_heading:
            extracted_data[current_heading].append(stripped_line)

        # if heading_count > max_headings:  # Stop processing further lines
        #     break
        

    # for heading, content in extracted_data.items():
    #     # print(heading)
    #     # print("-" * 50)
    #     # print("\n".join(content))  # Print content under the heading
    #     # print("\n")
    #     sentences = split_sentences(content)  # Split the content into sentences
    #     for sentence in sentences:
    #         print(sentence)
        
    # Process extracted data
    for heading, content in extracted_data.items():
        # Ensure content is a string
        if isinstance(content, list):
            content = " ".join(content)  # Convert list to a single string

        sentences = split_sentences(content)  # Split the content into sentences
        for sentence in sentences:
            # print(heading)  # Print the heading before every sentence
            # print()
            # print(sentence)
            # print("\n")  # Add a blank line for readability
            # Save structured
            structured_data.append((heading, sentence))

    for entry in structured_data:
        print(entry)

extract_content_under_headings(text_file_path,0)

with open("structured_data.json", "w", encoding="utf-8") as f:
    json.dump(structured_data, f, ensure_ascii=False, indent=4)

print("Data successfully saved to structured_data.json")


# save_pages(text_file_path)

