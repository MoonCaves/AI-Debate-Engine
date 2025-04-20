import os
import openai
import time
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define personality templates
PERSONALITIES = {
    "goggins": {
        "name": "David Goggins",
        "system_prompt": """You are David Goggins. Speak in his intense, direct, and brutally honest style. 
Prioritize mental toughness, taking ownership, and pushing through limitations. 
Use short, powerful sentences. Swear occasionally for emphasis. 
Challenge excuses and promote extreme ownership and accountability.
Stay completely in character throughout this debate."""
    },
    "robbins": {
        "name": "Mel Robbins",
        "system_prompt": """You are Mel Robbins. Speak in her warm, casual, and motivating style.
Focus on practical habits, self-compassion, and celebrating small wins.
Use the 5-Second Rule concept when appropriate. Be encouraging but realistic.
Maintain a conversational tone with occasional personal anecdotes.
Stay completely in character throughout this debate."""
    }
}

# Define debate rounds structure
DEBATE_ROUNDS = [
    {"title": "Opening Statement", "instruction": "Present your opening perspective on this topic."},
    {"title": "Pushback / Attack", "instruction": "Challenge the opposing view and defend your position."},
    {"title": "Clarify & Reflect", "instruction": "Reflect on the discussion and clarify your final position."}
]

def get_ai_response(system_prompt, user_prompt, model="gpt-4o"):
    """Get response from OpenAI API"""
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

def generate_summary(debate_history, model="gpt-4o"):
    """Generate summary of the debate"""
    summary_prompt = f"""Below is a debate between two personalities:

{json.dumps(debate_history, indent=2)}

Analyze how each personality's thinking evolved throughout the debate. For each personality, provide:
1. Their starting position
2. How their thinking changed during the debate
3. Points where they held firm
4. Why they shifted or maintained their positions

Format the summary in a clear, readable structure."""

    system_prompt = "You are a neutral debate analyst. Provide an objective summary of how each debater's thinking evolved."
    
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
        return "Error: Could not generate summary."

def run_debate():
    """Run the AI debate engine"""
    # Get user inputs
    print("\n=== AI DEBATE ENGINE ===\n")
    
    # Get debate topic
    topic = input("Enter the debate topic/problem: ")
    
    # Display personality options
    print("\nAvailable personalities:")
    for key, value in PERSONALITIES.items():
        print(f"- {value['name']} ({key})")
    
    # Select personalities
    personality_a_key = input("\nSelect Fighter A (enter key): ").lower()
    while personality_a_key not in PERSONALITIES:
        personality_a_key = input("Invalid selection. Select Fighter A (enter key): ").lower()
    
    personality_b_key = input("Select Fighter B (enter key): ").lower()
    while personality_b_key not in PERSONALITIES or personality_b_key == personality_a_key:
        personality_b_key = input("Invalid selection. Select Fighter B (enter key): ").lower()
    
    # Select who leads
    leader = input(f"\nWho leads the debate? (A for {PERSONALITIES[personality_a_key]['name']}, B for {PERSONALITIES[personality_b_key]['name']}): ").upper()
    while leader not in ['A', 'B']:
        leader = input("Invalid selection. Who leads the debate? (A/B): ").upper()
    
    personality_a = PERSONALITIES[personality_a_key]
    personality_b = PERSONALITIES[personality_b_key]
    
    print(f"\n=== DEBATE: {personality_a['name']} vs {personality_b['name']} ===")
    print(f"Topic: {topic}")
    print(f"Leading: {'Fighter A' if leader == 'A' else 'Fighter B'} ({personality_a['name'] if leader == 'A' else personality_b['name']})")
    print("\nStarting debate...\n")
    
    # Initialize debate history
    debate_history = {
        "topic": topic,
        "fighter_a": {
            "name": personality_a["name"],
            "responses": []
        },
        "fighter_b": {
            "name": personality_b["name"],
            "responses": []
        }
    }
    
    # Run the debate rounds
    for round_idx, round_info in enumerate(DEBATE_ROUNDS):
        print(f"\n--- ROUND {round_idx + 1}: {round_info['title']} ---\n")
        
        # Determine who goes first in this round
        if (leader == 'A' and round_idx % 2 == 0) or (leader == 'B' and round_idx % 2 == 1):
            first = 'A'
            second = 'B'
        else:
            first = 'B'
            second = 'A'
        
        # First debater's turn
        first_personality = personality_a if first == 'A' else personality_b
        first_opponent = personality_b if first == 'A' else personality_a
        
        # Construct prompt based on debate history
        first_prompt = f"Topic: {topic}\n\nRound: {round_info['title']}\n\nInstruction: {round_info['instruction']}\n\n"
        
        # Add context from previous rounds if available
        if round_idx > 0:
            first_prompt += "Previous exchanges:\n"
            for i in range(round_idx):
                if first == 'A':
                    first_prompt += f"Round {i+1} - You: {debate_history['fighter_a']['responses'][i]['content']}\n"
                    first_prompt += f"Round {i+1} - Opponent: {debate_history['fighter_b']['responses'][i]['content']}\n\n"
                else:
                    first_prompt += f"Round {i+1} - You: {debate_history['fighter_b']['responses'][i]['content']}\n"
                    first_prompt += f"Round {i+1} - Opponent: {debate_history['fighter_a']['responses'][i]['content']}\n\n"
        
        first_prompt += f"\nYou are {first_personality['name']}. {round_info['instruction']} Remember to stay completely in character."
        
        # Get first debater's response
        print(f"{first_personality['name']}'s turn...")
        first_response = get_ai_response(first_personality['system_prompt'], first_prompt)
        
        # Store response in debate history
        if first == 'A':
            debate_history['fighter_a']['responses'].append({"round": round_idx + 1, "title": round_info['title'], "content": first_response})
        else:
            debate_history['fighter_b']['responses'].append({"round": round_idx + 1, "title": round_info['title'], "content": first_response})
        
        # Display response
        print(f"\n{first_personality['name']}:\n{first_response}\n")
        
        # Second debater's turn
        second_personality = personality_b if second == 'B' else personality_a
        
        # Construct prompt for second debater
        second_prompt = f"Topic: {topic}\n\nRound: {round_info['title']}\n\nInstruction: {round_info['instruction']}\n\n"
        
        # Add context from previous rounds
        if round_idx > 0:
            second_prompt += "Previous exchanges:\n"
            for i in range(round_idx):
                if second == 'A':
                    second_prompt += f"Round {i+1} - You: {debate_history['fighter_a']['responses'][i]['content']}\n"
                    second_prompt += f"Round {i+1} - Opponent: {debate_history['fighter_b']['responses'][i]['content']}\n\n"
                else:
                    second_prompt += f"Round {i+1} - You: {debate_history['fighter_b']['responses'][i]['content']}\n"
                    second_prompt += f"Round {i+1} - Opponent: {debate_history['fighter_a']['responses'][i]['content']}\n\n"
        
        # Add current round's first response
        second_prompt += f"Opponent's current response: {first_response}\n\n"
        second_prompt += f"\nYou are {second_personality['name']}. {round_info['instruction']} Respond to your opponent's points. Remember to stay completely in character."
        
        # Get second debater's response
        print(f"{second_personality['name']}'s turn...")
        second_response = get_ai_response(second_personality['system_prompt'], second_prompt)
        
        # Store response in debate history
        if second == 'A':
            debate_history['fighter_a']['responses'].append({"round": round_idx + 1, "title": round_info['title'], "content": second_response})
        else:
            debate_history['fighter_b']['responses'].append({"round": round_idx + 1, "title": round_info['title'], "content": second_response})
        
        # Display response
        print(f"\n{second_personality['name']}:\n{second_response}\n")
        
        # Small delay between rounds
        if round_idx < len(DEBATE_ROUNDS) - 1:
            print("Moving to next round...")
            time.sleep(2)
    
    # Generate and display summary
    print("\n=== DEBATE SUMMARY ===\n")
    print("Generating summary...")
    summary = generate_summary(debate_history)
    print(f"\n{summary}\n")
    
    print("\n=== DEBATE COMPLETED ===\n")
    
    # Option to save debate to file
    save = input("Save this debate to file? (y/n): ").lower()
    if save == 'y':
        filename = f"debate_{int(time.time())}.txt"
        with open(filename, 'w') as f:
            f.write(f"DEBATE: {personality_a['name']} vs {personality_b['name']}\n")
            f.write(f"Topic: {topic}\n\n")
            
            for round_idx, round_info in enumerate(DEBATE_ROUNDS):
                f.write(f"--- ROUND {round_idx + 1}: {round_info['title']} ---\n\n")
                
                # Fighter A's response for this round
                f.write(f"{personality_a['name']}:\n")
                for response in debate_history['fighter_a']['responses']:
                    if response['round'] == round_idx + 1:
                        f.write(f"{response['content']}\n\n")
                
                # Fighter B's response for this round
                f.write(f"{personality_b['name']}:\n")
                for response in debate_history['fighter_b']['responses']:
                    if response['round'] == round_idx + 1:
                        f.write(f"{response['content']}\n\n")
            
            f.write("=== SUMMARY ===\n\n")
            f.write(summary)
        
        print(f"Debate saved to {filename}")

if __name__ == "__main__":
    run_debate()