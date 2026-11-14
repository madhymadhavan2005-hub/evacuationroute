import matplotlib
matplotlib.use('Agg')

import streamlit as st
import networkx as nx
import math
import matplotlib.pyplot as plt
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Multi-Hazard Evacuation Command Center",
    page_icon="🚨",
    layout="wide"
)

# --- Custom High-Impact CSS Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .hero-banner {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid #374151;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .hero-title {
        color: #f3f4f6;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        color: #9ca3af;
        font-size: 1.05rem;
        line-height: 1.5;
    }
    .card {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 18px;
        border-radius: 10px;
        margin-bottom: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Hero Header ---
st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🚨 Multi-Hazard AI Emergency Evacuation Planner</div>
        <div class="hero-subtitle">
            Tactical Command Center simulating dynamic disaster propagation (Fire, Flood, Landslide) 
            and real-time A* route optimization for emergency response teams.
        </div>
    </div>
""", unsafe_allow_html=True)

GRID_SIZE = 12

# --- Session State Initialization ---
if "start_point" not in st.session_state:
    st.session_state.start_point = (0, 0)
if "dest_point" not in st.session_state:
    st.session_state.dest_point = (11, 11)

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

    # 2. Flood spreads horizontally and downward
    new_floods = set(st.session_state.floods)
    for wx, wy in st.session_state.floods:
        for dx, dy in [(1, 0), (-1, 0), (0, -1)]:
            nx_node, ny_node = wx + dx, wy + dy
            if 0 <= nx_node < GRID_SIZE and 0 <= ny_node < GRID_SIZE:
                if (nx_node, ny_node) not in protected:
                    new_floods.add((nx_node, ny_node))
    st.session_state.floods = new_floods

    st.session_state.step_count += 1

# --- Sidebar Controls ---
with st.sidebar:
    st.markdown("### 📍 1. Routing Parameters")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sx = st.number_input("Start X", 0, GRID_SIZE - 1, st.session_state.start_point[0])
    with col_s2:
        sy = st.number_input("Start Y", 0, GRID_SIZE - 1, st.session_state.start_point[1])

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        dx = st.number_input("Dest X", 0, GRID_SIZE - 1, st.session_state.dest_point[0])
    with col_d2:
        dy = st.number_input("Dest Y", 0, GRID_SIZE - 1, st.session_state.dest_point[1])

    if st.button("Update Coordinates", use_container_width=True):
        st.session_state.start_point = (int(sx), int(sy))
        st.session_state.dest_point = (int(dx), int(dy))
        for pt in [st.session_state.start_point, st.session_state.dest_point]:
            st.session_state.fires.discard(pt)
            st.session_state.floods.discard(pt)
            st.session_state.landslides.discard(pt)
        st.rerun()

    st.divider()
    st.markdown("### ⚠️ 2. Hazard Management")
    hazard_type = st.selectbox(
        "Select Hazard",
        ["🔥 Fire (Expanding)", "🌊 Flood (Flowing)", "🪨 Landslide (Blockade)"]
    )
    
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        hx = st.number_input("X Coord", 0, GRID_SIZE - 1, 5)
    with col_h2:
        hy = st.number_input("Y Coord", 0, GRID_SIZE - 1, 5)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Deploy", use_container_width=True):
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
                st.warning("Cannot target Start/Shelter!")
    with col_btn2:
        if st.button("Clear", use_container_width=True):
            pt = (int(hx), int(hy))
            st.session_state.fires.discard(pt)
            st.session_state.floods.discard(pt)
            st.session_state.landslides.discard(pt)
            st.rerun()

    st.divider()
    st.markdown("### ⏱️ 3. Simulation Control")
    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        if st.button("⏭️ Step", use_container_width=True):
            advance_hazards()
            st.rerun()
    with col_sim2:
        live_label = "⏸️ Pause" if st.session_state.live_sim else "▶️ Auto-Run"
        if st.button(live_label, use_container_width=True):
            st.session_state.live_sim = not st.session_state.live_sim
            st.rerun()

    if st.button("🔄 Reset Command Grid", use_container_width=True):
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

# --- Top Status Metrics Bar ---
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("⏱️ Sim Step", f"Step {st.session_state.step_count}")
m2.metric("🔥 Fire Cells", len(st.session_state.fires))
m3.metric("🌊 Flood Cells", len(st.session_state.floods))
m4.metric("🪨 Landslides", len(st.session_state.landslides))
m5.metric("🛡️ Path Status", f"{len(evac_path)-1} Steps" if evac_path else "BLOCKED ❌")

st.markdown("<br>", unsafe_allow_html=True)

# --- Main Grid Map & Route Info Panel ---
col_map, col_info = st.columns([1.6, 1])

with col_map:
    fig, ax = plt.subplots(figsize=(7, 7))
    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#0e1117")

    pos = {node: node for node in G.nodes()}

    # Grid layout rendering
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=240, node_color="#1f2937")
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#30363d", width=1.2)

    # Active Path
    if evac_path:
        path_edges = list(zip(evac_path[:-1], evac_path[1:]))
        nx.draw_networkx_edges(
            G, pos, ax=ax, edgelist=path_edges,
            edge_color="#10b981", width=5.0, label="Safe Evacuation Route"
        )

    # Hazards
    if st.session_state.fires:
        nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=list(st.session_state.fires), node_size=360, node_color="#ef4444", node_shape="o", label="🔥 Fire Zone")
    if st.session_state.floods:
        nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=list(st.session_state.floods), node_size=360, node_color="#3b82f6", node_shape="s", label="🌊 Flood Zone")
    if st.session_state.landslides:
        nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=list(st.session_state.landslides), node_size=360, node_color="#d97706", node_shape="^", label="🪨 Landslide")

    # Start & Destination Markers
    nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=[st.session_state.start_point], node_size=460, node_color="#facc15", label="🚩 Evacuee Start")
    nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=[st.session_state.dest_point], node_size=480, node_color="#22c55e", label="🏥 Safe Shelter")

    labels = {node: f"{node[0]},{node[1]}" for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, ax=ax, font_size=6, font_color="#9ca3af")

    legend = ax.legend(loc="upper left", facecolor="#161b22", edgecolor="#30363d", fontsize=8)
    for text in legend.get_texts():
        text.set_color("#f3f4f6")

    ax.axis("off")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with col_info:
    st.markdown("### 🧭 Mission Telemetry")
    st.markdown(f"""
    <div class="card">
        <b>Start Coordinates:</b> <code>{st.session_state.start_point}</code><br>
        <b>Shelter Destination:</b> <code>{st.session_state.dest_point}</code>
    </div>
    """, unsafe_allow_html=True)

    if evac_path:
        st.markdown(f"""
        <div class="card" style="border-left: 4px solid #10b981;">
            <h4 style="color: #10b981; margin:0 0 8px 0;">✅ Optimal Route Computed</h4>
            <p style="margin:0; font-size:0.9rem; color:#9ca3af;">Total steps required to reach safety: <b>{len(evac_path) - 1} nodes</b></p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**Waypoint Trajectory:**")
        st.code(" -> ".join([str(step) for step in evac_path]), language="text")
    else:
        st.markdown("""
        <div class="card" style="border-left: 4px solid #ef4444;">
            <h4 style="color: #ef4444; margin:0 0 8px 0;">❌ Route Severed / Blocked</h4>
            <p style="margin:0; font-size:0.9rem; color:#9ca3af;">All network conduits compromised by environmental hazards. Re-routing failed.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📊 Disaster Physics Rules")
    st.markdown("""
    <div class="card" style="font-size:0.85rem; color:#9ca3af;">
        • <b>Fire:</b> Cardinal expansion per clock cycle.<br>
        • <b>Flood:</b> Lateral and downward fluid flow.<br>
        • <b>Landslide:</b> Permanent geographic obstruction.
    </div>
    """, unsafe_allow_html=True)

# --- Live Simulation Handler ---
if st.session_state.live_sim:
    time.sleep(1.2)
    advance_hazards()
    st.rerun()