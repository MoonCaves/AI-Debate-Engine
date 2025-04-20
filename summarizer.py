"""
AI Debate Engine - Summarizer Module
Handles generating insightful summaries of debates.
"""

import os
import json
import openai

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_summary(debate_history, fighter_a_name, fighter_b_name, model="gpt-4o"):
    """Generate an insightful summary of the debate"""
    
    # Prepare a clean version of the debate history for the summary
    clean_history = {
        "topic": debate_history["topic"],
        "leader": debate_history.get("leader", "A"),  # Default to A if not specified
        "rounds": []
    }
    
    round_names = ["Opening Statement", "Pushback / Attack", "Clarify & Reflect"]
    
    for i, round_data in enumerate(debate_history["rounds"]):
        # Get who was first and second in this round
        first_fighter = round_data["first"]["fighter"]  # 'A' or 'B'
        second_fighter = round_data["second"]["fighter"]  # 'A' or 'B'
        
        # Get their responses
        first_response = round_data["first"]["response"]
        second_response = round_data["second"]["response"]
        
        # Create clean record of this round
        clean_round = {
            "round_name": round_names[i],
            "fighter_a_response": first_response if first_fighter == "A" else second_response,
            "fighter_b_response": second_response if first_fighter == "A" else first_response,
            "first_speaker": fighter_a_name if first_fighter == "A" else fighter_b_name
        }
            
        clean_history["rounds"].append(clean_round)
    
    # Determine who led the debate
    leader_fighter = clean_history["leader"]  # 'A' or 'B'
    leader_name = fighter_a_name if leader_fighter == "A" else fighter_b_name
    
    # Create the summary prompt
    summary_prompt = f"""Analyze this debate between {fighter_a_name} and {fighter_b_name} on the topic: {debate_history['topic']}

{json.dumps(clean_history, indent=2)}

Don't use a generic template for your analysis. Instead, provide an insightful summary that:

1. Identifies the core philosophical differences between the debaters
2. Highlights the most powerful arguments from each side
3. Analyzes how the opening framing influenced the debate direction (Note: {leader_name} led the debate and spoke first in the opening round)
4. Notes any moments where either debater had to adapt their philosophy to the situation
5. Identifies which specific phrases, metaphors, or examples were most effectively deployed

FORMAT:
- Use a compelling title that captures the essence of the philosophical clash
- Provide clear, direct analysis of each point above
- End with a brief reflection on how these contrasting approaches represent different paths to handling the same challenge"""
    
    system_prompt = "You are a debate analyst with expertise in philosophy, rhetoric, and psychology. Your job is to provide insightful analysis of debates between AI personalities, highlighting the clash of philosophies and rhetorical strategies."
    
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Error: Could not generate debate summary."