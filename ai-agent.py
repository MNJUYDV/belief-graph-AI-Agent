# This simulates a naive reasoning agent

belief = "The cheapest flight is $218"
confidence = 0.95

# New evidence arrives
new_price = 347
confidence_new = 0.99

# The agent ignores contradiction
print("Agent belief:", belief)
print("Agent confidence:", confidence)
print("New evidence price:", new_price)
print("New evidence confidence:", confidence_new)

# Agent proceeds anyway
print("\nAction: Book flight for $218")
