"""
AI Debate Engine - Utility Functions
Helper functions for file loading, personality management, etc.
"""

import os

def list_personalities():
    """List all available personality files"""
    personality_dir = os.path.join(os.path.dirname(__file__), "personalities")
    personalities = []
    
    for filename in os.listdir(personality_dir):
        if filename.endswith(".txt"):
            personalities.append(filename[:-4])  # Remove .txt extension
            
    return personalities

def load_personality(name):
    """Load a personality from its definition file"""
    print(f"DEBUG: Loading personality: {name}")
    personality_path = os.path.join(os.path.dirname(__file__), "personalities", f"{name}.txt")
    
    if not os.path.exists(personality_path):
        error_msg = f"Personality file not found: {name}.txt"
        print(f"ERROR: {error_msg}")
        raise ValueError(error_msg)
    
    with open(personality_path, 'r') as f:
        content = f.read()
    
    print(f"DEBUG: Loaded personality file with {len(content)} characters")
    
    # Parse sections (NAME, SYSTEM_PROMPT, etc.)
    sections = {}
    current_section = None
    section_content = ""
    
    for line in content.split('\n'):
        if ':' in line and line.split(':')[0].isupper() and not line.startswith('-'):
            # Save previous section if it exists
            if current_section:
                sections[current_section] = section_content.strip()
            
            # Start new section
            current_section = line.split(':')[0]
            section_content = line.split(':', 1)[1].strip()
        elif current_section:
            section_content += '\n' + line
    
    # Save the last section
    if current_section:
        sections[current_section] = section_content.strip()
    
    # Ensure required sections exist
    required_sections = ["NAME", "SYSTEM_PROMPT"]
    for section in required_sections:
        if section not in sections:
            error_msg = f"Missing required section in personality file: {section}"
            print(f"ERROR: {error_msg}")
            raise ValueError(error_msg)
    
    print(f"DEBUG: Successfully parsed personality: {sections['NAME']}")
    return sections {name}.txt")
    
    with open(personality_path, 'r') as f:
        content = f.read()
    
    # Parse sections (NAME, SYSTEM_PROMPT, etc.)
    sections = {}
    current_section = None
    section_content = ""
    
    for line in content.split('\n'):
        if ':' in line and line.split(':')[0].isupper() and not line.startswith('-'):
            # Save previous section if it exists
            if current_section:
                sections[current_section] = section_content.strip()
            
            # Start new section
            current_section = line.split(':')[0]
            section_content = line.split(':', 1)[1].strip()
        elif current_section:
            section_content += '\n' + line
    
    # Save the last section
    if current_section:
        sections[current_section] = section_content.strip()
    
    # Ensure required sections exist
    required_sections = ["NAME", "SYSTEM_PROMPT"]
    for section in required_sections:
        if section not in sections:
            raise ValueError(f"Missing required section in personality file: {section}")
    
    return sections

def load_prompt_template(round_type):
    """Load a prompt template for a specific round type"""
    template_path = os.path.join(os.path.dirname(__file__), "prompts", f"{round_type}.txt")
    
    if not os.path.exists(template_path):
        raise ValueError(f"Prompt template not found: {round_type}.txt")
    
    with open(template_path, 'r') as f:
        template = f.read()
    
    return template