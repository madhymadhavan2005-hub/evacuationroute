import matplotlib
matplotlib.use('Agg')

import streamlit as st
import networkx as nx
import math
import matplotlib.pyplot as plt
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Multi-Hazard Evacuation Route Planner",
    page_icon="🚨",
    layout="wide"
)

st.title("🚨 Multi-Hazard AI Emergency Evacuation Route Planner")
st.write("Configure custom start/destination points and deploy specific hazards (Fire, Flood, Landslide) to compute safe A* evacuation paths.")

GRID_SIZE = 12

# --- Session State Initialization ---
if "start_point" not in st.session_state:
    st.session_state.start_point = (0, 0)
if "dest_point" not in st.session_state:
    st.session_state.dest_point = (11, 11)

# Separate hazard sets with unique disaster physics
if "fires" not in st.session_state:
    st.session_state.fires = {(4, 4), (4, 5)}
if "floods" not in st.session_state:
    st.session_state.floods = {(2, 7), (2, 8), (3, 8)}
if "landslides" not in st.session_state:
    st.session_state.landslides = {(7, 3), (8, 3), (8, 4)}

if "live_sim" not in st.session_state:
    st.session_state.live_sim = False
if "step_count" not in st.session_state:
    st.session_state.step_count = 0

# --- Hazard Propagation Physics ---
def advance_hazards():
    protected = {st.session_state.dest_point}
    
    # 1. Fire spreads rapidly in all 4 cardinal directions
    new_fires = set(st.session_state.fires)
    for fx, fy in st.session_state.fires:
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx_node, ny_node = fx + dx, fy + dy
            if 0 <= nx_node < GRID_SIZE and 0 <= ny_node < GRID_SIZE:
                if (nx_node, ny_node) not in protected:
                    new_fires.add((nx_node, ny_node))
    st.session_state.fires = new_fires

    # 2. Flood spreads horizontally and downward (flowing water behavior)
    new_floods = set(st.session_state.floods)
    for wx, wy in st.session_state.floods:
        for dx, dy in [(1, 0), (-1, 0), (0, -1)]:
            nx_node, ny_node = wx + dx, wy + dy
            if 0 <= nx_node < GRID_SIZE and 0 <= ny_node < GRID_SIZE:
                if (nx_node, ny_node) not in protected:
                    new_floods.add((nx_node, ny_node))
    st.session_state.floods = new_floods

    # 3. Landslide is a static structural blockage (does not spread outward)
    st.session_state.step_count += 1

# --- Sidebar Controls ---
with st.sidebar:
    st.header("📍 1. Start & Destination")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sx = st.number_input("Start X", 0, GRID_SIZE - 1, st.session_state.start_point[0])
    with col_s2:
        sy = st.number_input("Start Y", 0, GRID_SIZE - 1, st.session_state.start_point[1])

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        dx = st.number_input("Destination X", 0, GRID_SIZE - 1, st.session_state.dest_point[0])
    with col_d2:
        dy = st.number_input("Destination Y", 0, GRID_SIZE - 1, st.session_state.dest_point[1])

    if st.button("Set Start & Destination", use_container_width=True):
        st.session_state.start_point = (int(sx), int(sy))
        st.session_state.dest_point = (int(dx), int(dy))
        # Ensure start/dest aren't covered by existing hazards
        for pt in [st.session_state.start_point, st.session_state.dest_point]:
            st.session_state.fires.discard(pt)
            st.session_state.floods.discard(pt)
            st.session_state.landslides.discard(pt)
        st.rerun()

    st.divider()
    st.header("⚠️ 2. Place / Remove Hazards")
    hazard_type = st.selectbox(
        "Select Hazard Type",
        ["🔥 Fire (Spreads all directions)", "🌊 Flood (Spreads laterally/down)", "🪨 Landslide (Permanent roadblock)"]
    )
    
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        hx = st.number_input("Hazard X", 0, GRID_SIZE - 1, 5)
    with col_h2:
        hy = st.number_input("Hazard Y", 0, GRID_SIZE - 1, 5)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Add Hazard", use_container_width=True):
            pt = (int(hx), int(hy))
            if pt not in {st.session_state.start_point, st.session_state.dest_point}:
                if "Fire" in hazard_type:
                    st.session_state.fires.add(pt)
                elif "Flood" in hazard_type:
                    st.session_state.floods.add(pt)
                else:
                    st.session_state.landslides.add(pt)
                st.rerun()
            else:
                st.warning("Cannot place hazard on Start or Destination!")
    with col_btn2:
        if st.button("Remove Hazard", use_container_width=True):
            pt = (int(hx), int(hy))
            st.session_state.fires.discard(pt)
            st.session_state.floods.discard(pt)
            st.session_state.landslides.discard(pt)
            st.rerun()

    st.divider()
    st.header("⏱️ 3. Simulation Engine")
    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        if st.button("⏭️ Step Spread", use_container_width=True):
            advance_hazards()
            st.rerun()
    with col_sim2:
        live_label = "⏸️ Pause" if st.session_state.live_sim else "▶️ Live Run"
        if st.button(live_label, use_container_width=True):
            st.session_state.live_sim = not st.session_state.live_sim
            st.rerun()

    if st.button("🔄 Reset Entire Map", use_container_width=True):
        st.session_state.live_sim = False
        st.session_state.step_count = 0
        st.session_state.start_point = (0, 0)
        st.session_state.dest_point = (11, 11)
        st.session_state.fires = {(4, 4), (4, 5)}
        st.session_state.floods = {(2, 7), (2, 8), (3, 8)}
        st.session_state.landslides = {(7, 3), (8, 3), (8, 4)}
        st.rerun()

# --- Graph Construction & A* Pathfinding ---
G = nx.grid_2d_graph(GRID_SIZE, GRID_SIZE)
for u, v in G.edges():
    G[u][v]["weight"] = 1.0

# Combine all active hazards and block edges connected to them
all_hazards = st.session_state.fires | st.session_state.floods | st.session_state.landslides
for h_node in all_hazards:
    if G.has_node(h_node):
        for neighbor in G.neighbors(h_node):
            G[h_node][neighbor]["weight"] = float("inf")
            G[neighbor][h_node]["weight"] = float("inf")

def heuristic(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

evac_path = None
try:
    evac_path = nx.astar_path(
        G,
        source=st.session_state.start_point,
        target=st.session_state.dest_point,
        heuristic=heuristic,
        weight="weight"
    )
except nx.NetworkXNoPath:
    evac_path = None

# --- Top Status Bar ---
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Simulation Step", f"Step {st.session_state.step_count}")
m2.metric("🔥 Fire Cells", len(st.session_state.fires))
m3.metric("🌊 Flood Cells", len(st.session_state.floods))
m4.metric("🪨 Landslide Cells", len(st.session_state.landslides))
m5.metric("Evacuation Status", f"{len(evac_path)-1} Steps" if evac_path else "BLOCKED")

st.divider()

# --- Main Grid & Route Details ---
col_map, col_info = st.columns([2, 1])

with col_map:
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#0e1117")

    pos = {node: node for node in G.nodes()}

    # Draw base grid
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=220, node_color="#1f2937")
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#374151", width=1.2)

    # Draw Evacuation Path
    if evac_path:
        path_edges = list(zip(evac_path[:-1], evac_path[1:]))
        nx.draw_networkx_edges(
            G, pos, ax=ax, edgelist=path_edges,
            edge_color="#10b981", width=4.5, label="Safe Evacuation Path"
        )

    # Draw Specific Hazards with Distinct Colors & Shapes
    if st.session_state.fires:
        nx.draw_networkx_nodes(
            G, pos, ax=ax, nodelist=list(st.session_state.fires),
            node_size=340, node_color="#ef4444", node_shape="o", label="🔥 Fire"
        )
    if st.session_state.floods:
        nx.draw_networkx_nodes(
            G, pos, ax=ax, nodelist=list(st.session_state.floods),
            node_size=340, node_color="#3b82f6", node_shape="s", label="🌊 Flood"
        )
    if st.session_state.landslides:
        nx.draw_networkx_nodes(
            G, pos, ax=ax, nodelist=list(st.session_state.landslides),
            node_size=340, node_color="#d97706", node_shape="^", label="🪨 Landslide"
        )

    # Draw Start & Destination
    nx.draw_networkx_nodes(
        G, pos, ax=ax, nodelist=[st.session_state.start_point],
        node_size=420, node_color="#facc15", label="🚩 Start Point"
    )
    nx.draw_networkx_nodes(
        G, pos, ax=ax, nodelist=[st.session_state.dest_point],
        node_size=450, node_color="#22c55e", label="🏥 Destination Shelter"
    )

    # Coordinate labels on nodes
    labels = {node: f"{node[0]},{node[1]}" for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, ax=ax, font_size=7, font_color="#cbd5e1")

    legend = ax.legend(loc="upper left", facecolor="#111827", edgecolor="#374151", fontsize=8)
    for text in legend.get_texts():
        text.set_color("white")

    ax.axis("off")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with col_info:
    st.subheader("🧭 Evacuation Route Details")
    st.write(f"**Start Coordinate:** `{st.session_state.start_point}`")
    st.write(f"**Destination Coordinate:** `{st.session_state.dest_point}`")
    st.divider()

    if evac_path:
        st.success(f"✅ Safe Evacuation Route Active ({len(evac_path) - 1} steps)")
        st.markdown("**Step-by-Step Coordinates:**")
        st.code(" -> ".join([str(step) for step in evac_path]), language="text")
    else:
        st.error("❌ NO SAFE ROUTE AVAILABLE!")
        st.warning("All paths between your start point and destination are blocked by Fire, Flood, or Landslide zones. Try removing a hazard or moving your start/destination.")

    st.divider()
    st.markdown("**Hazard Behavior Legend:**")
    st.markdown("- **🔥 Fire (Red Circle):** Expands in all 4 directions per step.")
    st.markdown("- **🌊 Flood (Blue Square):** Spreads sideways and downward per step.")
    st.markdown("- **🪨 Landslide (Brown Triangle):** Static debris blockage that stays fixed.")

# --- Live Simulation Loop ---
if st.session_state.live_sim:
    time.sleep(1.2)
    advance_hazards()
    st.rerun()