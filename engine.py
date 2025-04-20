"""
AI Debate Engine - Core Engine Logic
Handles the debate flow, round management, and interaction with the API.
"""

import os
import openai
from utils import load_personality, load_prompt_template
from summarizer import generate_summary

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_response(system_prompt, user_prompt, model="gpt-4o"):
    """Get a response from the OpenAI API"""
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting AI response: {e}")
        return "Error: Could not generate response."

def format_prompt(round_type, fighter_id, topic, history=None, opponent_response=None):
    """Create a properly structured prompt for the given round type"""
    # Load template for this round type
    template = load_prompt_template(round_type)
    
    # Replace placeholders in template
    prompt = template.replace("{TOPIC}", topic)
    
    # Add previous exchanges if available
    previous_context = ""
    if history and len(history) > 0:
        previous_context = "Previous exchanges:\n\n"
        for past_round in history:
            # Figure out which response in this round belongs to this fighter
            my_response = ""
            opponent_response_in_history = ""
            
            if past_round['first']['fighter'] == fighter_id:
                my_response = past_round['first']['response']
                opponent_response_in_history = past_round['second']['response']
            else:
                my_response = past_round['second']['response']
                opponent_response_in_history = past_round['first']['response']
            
            previous_context += f"You: {my_response}\n\n"
            previous_context += f"Opponent: {opponent_response_in_history}\n\n"
    
    prompt = prompt.replace("{PREVIOUS_CONTEXT}", previous_context)
    
    # Add opponent's response if available
    if opponent_response:
        prompt = prompt.replace("{OPPONENT_RESPONSE}", f"Your opponent just said:\n\n{opponent_response}")
    else:
        prompt = prompt.replace("{OPPONENT_RESPONSE}", "")
    
    return prompt

def execute_round(round_type, fighter_a, fighter_b, leader, history, topic):
    """Execute a single debate round"""
    round_names = ["Opening Statement", "Pushback / Attack", "Clarify & Reflect"]
    round_idx = {"opening": 0, "rebuttal": 1, "closing": 2}[round_type]
    
    print(f"\n--- ROUND {round_idx + 1}: {round_names[round_idx]} ---\n")
    
    # Determine who goes first in this round
    first = 'A' 
    second = 'B'
    
    # Get first personality details
    first_personality = fighter_a if first == 'A' else fighter_b
    first_system_prompt = first_personality["SYSTEM_PROMPT"]
    first_name = first_personality["NAME"]
    
    # Generate prompt for first speaker
    first_prompt = format_prompt(
        round_type, 
        first, 
        topic, 
        history
    )
    
    # Get first response
    print(f"{first_name}'s turn...")
    first_response = generate_response(first_system_prompt, first_prompt)
    print(f"\n{first_name}:\n{first_response}\n")
    
    # Get second personality details
    second_personality = fighter_b if second == 'B' else fighter_a
    second_system_prompt = second_personality["SYSTEM_PROMPT"]
    second_name = second_personality["NAME"]
    
    # Generate prompt for second speaker
    second_prompt = format_prompt(
        round_type, 
        second, 
        topic, 
        history, 
        first_response
    )
    
    # Get second response
    print(f"{second_name}'s turn...")
    second_response = generate_response(second_system_prompt, second_prompt)
    print(f"\n{second_name}:\n{second_response}\n")
    
    return {
        'round_type': round_type,
        'first': {'fighter': first, 'response': first_response},
        'second': {'fighter': second, 'response': second_response}
    }

def run_debate(topic, personality_a_name, personality_b_name, leader='A'):
    """Run a complete debate with 3 rounds"""
    print(f"DEBUG: Loading personalities: {personality_a_name} and {personality_b_name}")
    print(f"DEBUG: Leader is: {leader}")
    
    # Load personalities
    fighter_a = load_personality(personality_a_name)
    fighter_b = load_personality(personality_b_name)
    
    print(f"DEBUG: Fighter A is: {fighter_a['NAME']}")
    print(f"DEBUG: Fighter B is: {fighter_b['NAME']}")
    
    # Initialize debate history
    history = {'topic': topic, 'rounds': [], 'leader': leader}
    
    # Run 3 rounds
    round_types = ["opening", "rebuttal", "closing"]
    for round_type in round_types:
        print(f"\nStarting {round_type} round...")
        round_result = execute_round(round_type, fighter_a, fighter_b, leader, history['rounds'], topic)
        history['rounds'].append(round_result)
        print(f"Completed {round_type} round.")
    
    # Generate summary
    print("\n=== GENERATING DEBATE SUMMARY ===\n")
    summary = generate_summary(history, fighter_a["NAME"], fighter_b["NAME"])
    
    return {'history': history, 'summary': summary}