import itertools

def generate_behavior_matrix():
    # Define the boolean flags and AI providers
    boolean_flags = ['refresh_data', 'refresh_diagrams', 'local_pdf', 'ai_generate']
    ai_providers = ['claude', 'openai']

    # Generate all combinations of boolean flags
    bool_combinations = list(itertools.product([False, True], repeat=len(boolean_flags)))

    # Initialize the matrix
    matrix = []

    # Generate permutations
    for bool_combo in bool_combinations:
        combo_dict = dict(zip(boolean_flags, bool_combo))
        if combo_dict['ai_generate']:
            for provider in ai_providers:
                full_combo = combo_dict.copy()
                full_combo['ai_provider'] = provider
                matrix.append(full_combo)
        else:
            combo_dict['ai_provider'] = None
            matrix.append(combo_dict)

    return matrix

def describe_behavior(combo):
    behaviors = []
    if combo['refresh_data']:
        behaviors.append("Fetch new JSON data")
    if combo['refresh_diagrams']:
        behaviors.append("Re-download diagrams")
    if combo['local_pdf']:
        behaviors.append("Use local PDF/image links")
    else:
        behaviors.append("Use remote URLs")
    if combo['ai_generate']:
        behaviors.append(f"Generate AI content using {combo['ai_provider']}")
        if combo['local_pdf']:
            behaviors.append("AI processes local PDFs")
        else:
            behaviors.append("AI processes JSON descriptions")
    else:
        behaviors.append("Use basic flashcard content")
    return ", ".join(behaviors)

# Generate and print the behavior matrix
behavior_matrix = generate_behavior_matrix()
for i, combo in enumerate(behavior_matrix, 1):
    print(f"Scenario {i}:")
    print(f"Flags: {combo}")
    print(f"Expected behavior: {describe_behavior(combo)}")
    print()

print(f"Total scenarios: {len(behavior_matrix)}")
