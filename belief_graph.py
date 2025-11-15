import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime

# Global directed graph for beliefs
G = nx.DiGraph()

# ----------------------------
#  Belief Creation
# ----------------------------

def add_belief(
    node_id: str,
    entity: str,
    predicate: str,
    value,
    confidence: float,
    source: str = "unknown",
    status: str = "active",
    auto_check: bool = True,
):
    """
    Add a belief node to the graph.
    """
    G.add_node(
        node_id,
        entity=entity,
        predicate=predicate,
        value=value,
        confidence=float(confidence),
        source=source,
        status=status,
        timestamp=str(datetime.now()),
    )
    print(f"➕ Added belief: {node_id}  {predicate}({entity})={value}  conf={confidence}")

    if auto_check:
        detect_and_handle_contradictions(node_id)


def add_support_edge(parent: str, child: str):
    """
    Parent belief supports child belief.
    If parent becomes weaker, child should also become less trusted.
    Direction: parent ─supports─> child
    """
    G.add_edge(parent, child, relation="supports")
    print(f"  🔗 Added support edge: {parent} ─supports→ {child}")


# ----------------------------
#  Contradiction Detection
# ----------------------------

def detect_and_handle_contradictions(new_node_id: str):
    """
    Check if the new belief contradicts any existing belief:
    same (entity, predicate), different value.
    """
    new_data = G.nodes[new_node_id]

    for node_id, data in G.nodes(data=True):
        if node_id == new_node_id:
            continue

        # Skip archived/outdated beliefs if you want, or include them
        if data.get("status") not in ("active", "outdated"):
            continue

        same_entity = data.get("entity") == new_data.get("entity")
        same_predicate = data.get("predicate") == new_data.get("predicate")
        different_value = data.get("value") != new_data.get("value")

        if same_entity and same_predicate and different_value:
            print(f"\n❌ Contradiction detected between {new_node_id} and {node_id}")
            G.add_edge(new_node_id, node_id, relation="contradicts")
            self_correct(new_node_id, node_id)


# ----------------------------
#  Self-Correction & Propagation
# ----------------------------

def reduce_confidence(node_id: str, factor: float = 0.6):
    old_conf = G.nodes[node_id]["confidence"]
    new_conf = round(old_conf * factor, 3)
    G.nodes[node_id]["confidence"] = new_conf
    print(f"   ↓ Confidence decayed for {node_id}: {old_conf} → {new_conf}")


def propagate_effects(node_id: str):
    """
    Propagate uncertainty only through 'supports' edges.
    Direction: node ─supports→ child
    """
    for _, child, rel in G.out_edges(node_id, data="relation"):
        if rel == "supports":
            print(f"   ↳ Propagating uncertainty to {child} (supported by {node_id})")
            # Slightly smaller decay for downstream beliefs
            reduce_confidence(child, factor=0.9)
            propagate_effects(child)

def ask(predicate: str, entity: str):
    """
    Query the most trusted current belief.
    Returns the highest-confidence 'active' belief.
    """
    candidates = [
        (node, data)
        for node, data in G.nodes(data=True)
        if data["entity"] == entity
        and data["predicate"] == predicate
        and data["status"] == "active"
    ]

    if not candidates:
        print(f"🤷 No trusted belief for {predicate}({entity})")
        return None

    # Return the belief with highest confidence
    best = max(candidates, key=lambda x: x[1]["confidence"])
    node, data = best

    print(f"💡 Query: {predicate}({entity})")
    print(f" → Current best belief: {data['value']} (conf={data['confidence']}) via {node}")

    return data["value"]



def self_correct(new_node: str, old_node: str):
    """
    Decide which belief to trust more, based on confidence.
    Demote the loser, propagate effects, update status.
    """
    new_conf = G.nodes[new_node]["confidence"]
    old_conf = G.nodes[old_node]["confidence"]

    if new_conf >= old_conf:
        winner, loser = new_node, old_node
    else:
        winner, loser = old_node, new_node

    print(f"🤖 Belief Update: {winner} is now trusted over {loser}")

    # Update statuses
    G.nodes[winner]["status"] = "active"
    G.nodes[loser]["status"] = "outdated"

    # Demote loser and propagate uncertainty through its support chain
    reduce_confidence(loser)
    propagate_effects(loser)
    archive_belief(loser)



# ----------------------------
#  Reliability Metric
# ----------------------------

def compute_reliability(entity: str, predicate: str):
    """
    Compute a simple reliability score for all beliefs
    about (entity, predicate).
    """
    cluster = [
        (node_id, data)
        for node_id, data in G.nodes(data=True)
        if data.get("entity") == entity and data.get("predicate") == predicate
    ]

    if not cluster:
        print(f"\n[Reliability] No beliefs for {predicate}({entity})")
        return

    active_confs = [
        d["confidence"] for _, d in cluster if d.get("status") == "active"
    ]
    max_conf = max(active_confs) if active_confs else 0.0

    # Count distinct values as a rough proxy for conflict
    values = {d["value"] for _, d in cluster}
    contradictions = max(0, len(values) - 1)

    # Simple scoring: penalize contradictions
    reliability_score = round(max_conf / (1 + 0.3 * contradictions), 3)

    print(f"\n[Reliability] {predicate}({entity})")
    print(f"  Beliefs: {[ (n, d['value'], d['confidence'], d['status']) for n, d in cluster ]}")
    print(f"  Distinct values: {values} (contradictions={contradictions})")
    print(f"  → Reliability score = {reliability_score}\n")

    return reliability_score


# ----------------------------
#  Visualization & Debug
# ----------------------------

def visualize_graph(title: str = "Belief State Graph"):
    pos = nx.spring_layout(G, seed=42)
    labels = {
        node: f"{node}\n{data['predicate']}({data['entity']})={data['value']}\nconf={data['confidence']:.2f}\nstatus={data['status']}"
        for node, data in G.nodes(data=True)
    }
    nx.draw(
        G,
        pos,
        with_labels=True,
        labels=labels,
        node_size=3500,
        node_color="lightblue",
        font_size=7,
    )

    edge_labels = nx.get_edge_attributes(G, "relation")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)

    plt.title(title)
    plt.tight_layout()
    plt.show()


def print_beliefs():
    print("\n🧠 Current Beliefs:")
    for node_id, data in G.nodes(data=True):
        print(
            f"  {node_id}: {data['predicate']}({data['entity']})={data['value']}, "
            f"conf={data['confidence']}, status={data['status']}, source={data['source']}"
        )
    print("")

def archive_belief(node_id: str):
    """
    Move outdated belief into archive state so it doesn't interfere with reasoning,
    but still remains as part of the memory history.
    """
    status = G.nodes[node_id].get("status")
    if status == "outdated":
        G.nodes[node_id]["status"] = "archived"
        print(f"📦 Archived belief: {node_id}")
    elif status == "archived":
        G.nodes[node_id]["status"] = "shadow_history"
        print(f"🕶️ Shifted to shadow_history: {node_id}")



# ----------------------------
#  DEMO
# ----------------------------

if __name__ == "__main__":
    # 1) Base belief: price of a specific flight
    add_belief(
        "belief_price_218",
        entity="Flight123",
        predicate="price",
        value=218,
        confidence=0.82,
        source="API#1",
    )

    # 2) Derived belief: cheapest price on a route (depends on the flight price)
    add_belief(
        "belief_cheapest_218",
        entity="Route_NYC_SF",
        predicate="cheapest_price",
        value=218,
        confidence=0.78,
        source="LLM_reasoning",
        auto_check=False,  # no contradictions expected here
    )
    add_support_edge("belief_price_218", "belief_cheapest_218")

    # 3) Plan that depends on the cheapest price
    add_belief(
        "plan_book_218",
        entity="BookingPlan",
        predicate="book_price",
        value=218,
        confidence=0.75,
        source="Planner",
        auto_check=False,
    )
    add_support_edge("belief_cheapest_218", "plan_book_218")

    print_beliefs()

    # Reliability before contradiction
    compute_reliability("Flight123", "price")

    # 4) New stronger evidence contradicting old price belief
    add_belief(
        "belief_price_347",
        entity="Flight123",
        predicate="price",
        value=347,
        confidence=0.95,
        source="API#2 (refreshed)",
    )

    # State after self-correction and propagation
    print_beliefs()

    # Reliability after contradiction resolution
    compute_reliability("Flight123", "price")

    ask("price", "Flight123")


    visualize_graph("After Self-Correction & Propagation")

