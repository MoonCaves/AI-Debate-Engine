# Create a dedicated function to run the debate
def start_debate(topic, fighter_a, fighter_b, leader):
    """Start the debate with the given parameters"""
    # Get fighter names for easier reference
    fighter_a_name = fighter_a.replace('_', ' ').title()
    fighter_b_name = fighter_b.replace('_', ' ').title()
    leader_name = fighter_a_name if leader == 'A' else fighter_b_name
    
    print(f"\n=== STARTING DEBATE: {fighter_a_name} vs {fighter_b_name} ===")
    print(f"Topic: {topic}")
    print(f"Leading Debater: {leader_name} (will speak first in opening round)")
    print("\nInitiating debate...\n")
    
    # Run the debate
    print(f"\nDEBUG: About to run debate with topic: {topic}")
    print(f"DEBUG: Fighter A: {fighter_a}, Fighter B: {fighter_b}")
    print(f"DEBUG: Leader selected: {leader} ({fighter_a_name if leader == 'A' else fighter_b_name})")
    
    debate_result = run_debate(topic, fighter_a, fighter_b, leader)
    
    # Save debate to file
    timestamp = int(time.time())
    filename = f"debate_{timestamp}.txt"
    with open(filename, 'w') as f:
        leader_name = fighter_a_name if leader == 'A' else fighter_b_name
        f.write(f"DEBATE: {fighter_a_name} vs {fighter_b_name}\n")
        f.write(f"Topic: {topic}\n")
        f.write(f"Leading Debater: {leader_name}\n\n")
        
        for round_idx, round_data in enumerate(debate_result['history']['rounds']):
            round_names = ["Opening Statement", "Pushback / Attack", "Clarify & Reflect"]
            f.write(f"--- ROUND {round_idx + 1}: {round_names[round_idx]} ---\n\n")
            
            first_name = fighter_a_name if round_data['first']['fighter'] == 'A' else fighter_b_name
            second_name = fighter_b_name if round_data['second']['fighter'] == 'B' else fighter_a_name
            
            f.write(f"{first_name}:\n{round_data['first']['response']}\n\n")
            f.write(f"{second_name}:\n{round_data['second']['response']}\n\n")
        
        f.write("=== SUMMARY ===\n\n")
        f.write(debate_result['summary'])
    
    print(f"\nDebate saved to {filename}")
    print("\n=== DEBATE COMPLETED ===\n")
    
    return debate_result