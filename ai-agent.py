# This demonstrates an AI agent using the belief graph system

from belief_graph import (
    add_belief,
    add_support_edge,
    ask,
    print_beliefs,
    compute_reliability,
)

print("=" * 60)
print("AI Agent with Belief Graph System")
print("=" * 60)

# Initial belief: cheapest flight is $218
print("\n📌 Initial Belief:")
add_belief(
    "belief_cheapest_218",
    entity="Route_NYC_SF",
    predicate="cheapest_price",
    value=218,
    confidence=0.95,
    source="Initial_Agent_Knowledge",
)

# Create a booking plan based on this belief
add_belief(
    "plan_book_218",
    entity="BookingPlan",
    predicate="book_price",
    value=218,
    confidence=0.92,
    source="Planner",
    auto_check=False,
)
add_support_edge("belief_cheapest_218", "plan_book_218")

print_beliefs()

# New evidence arrives: price is actually $347
print("\n🆕 New Evidence Arrives:")
new_price = 347
confidence_new = 0.99

add_belief(
    "belief_cheapest_347",
    entity="Route_NYC_SF",
    predicate="cheapest_price",
    value=new_price,
    confidence=confidence_new,
    source="Updated_API_Data",
)

# Agent queries for current best belief before taking action
print("\n🤔 Agent queries belief before action:")
best_price = ask("cheapest_price", "Route_NYC_SF")

if best_price:
    print(f"\n✅ Action: Book flight for ${best_price}")

print_beliefs()

# Check reliability of the belief
compute_reliability("Route_NYC_SF", "cheapest_price")
