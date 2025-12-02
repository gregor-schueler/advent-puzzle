import streamlit as st
from solver import solve, WIDTH, HEIGHT, PIECE_BASES

st.set_page_config(layout="wide", page_title="4x6 Advent Puzzle Solver")

st.markdown(
    """
    <style>
        .hero {
            text-align: center;
            margin: 0 auto 2rem;
            max-width: 840px;
        }
        .hero h1 {
            margin-bottom: 0.5rem;
        }
        .hero p {
            margin: 0.25rem 0;
            color: #475467;
        }
        .hero ul {
            list-style: none;
            padding-left: 0;
            margin: 0.8rem 0 0;
        }
        .hero ul li {
            margin: 0.2rem 0;
        }
        .section-title {
            text-align: center;
            margin: 2rem 0 0.75rem;
        }
        .piece-strip {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 12px;
            margin-bottom: 1.5rem;
        }
        .piece-grid {
            display: grid;
            gap: 2px;
            background: #f4f4f4;
            padding: 6px;
            border-radius: 8px;
        }
        .target-wrapper {
            margin: 0 auto;
            max-width: 360px;
        }
        .target-wrapper p {
            text-align: center;
            color: #6b7280;
            margin-bottom: 0.75rem;
        }
        .target-hint {
            text-align: center;
            margin: 1rem auto 0;
            color: #475467;
            background: #f9fafb;
            border: 1px dashed #d1d5db;
            padding: 0.75rem 1rem;
            border-radius: 12px;
            max-width: 360px;
        }
        div[data-testid="stButton"] > button {
            border-radius: 12px;
            border: 1px solid #d1d5db;
            background: #f9fafb;
            color: #111827;
            height: 60px;
            font-size: 20px;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        div[data-testid="stButton"] > button:hover {
            border-color: #9ca3af;
            background: #ffffff;
        }
        div[data-testid="stButton"] > button[kind="primary"] {
            background: #0f172a;
            border-color: #0f172a;
            color: #ffffff;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.3);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------
# HTML/CSS Colors
# ----------------------
PIECE_COLORS_HTML = {
    "A": "#e74c3c",  # Red
    "B": "#2ecc71",  # Green
    "C": "#f1c40f",  # Yellow
    "D": "#3498db",  # Blue
    "E": "#9b59b6",  # Purple
    "F": "#1abc9c",  # Cyan
}

# ----------------------
# Page Header & Explanation
# ----------------------
st.markdown(
    """
    <div class="hero">
        <h1>🎄 4x6 Advent Puzzle Solver</h1>
        <p>Welcome to the <strong>4x6 Advent Puzzle</strong>!</p>
        <p><strong>Goal:</strong> Place all six unique pieces without overlap so that only your chosen target square remains open.</p>
        <ul>
            <li>Tap any grid cell to mark the <strong>target day</strong>.</li>
            <li>The solver instantly lists every tiling that avoids that square.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------
# Decorative piece shapes at top
# ----------------------
st.markdown("<h3 class='section-title'>🎨 Puzzle Pieces</h3>", unsafe_allow_html=True)
piece_html = "<div class='piece-strip'>"
for name, blocks in PIECE_BASES.items():
    # Render piece as mini-grid
    max_x = max(x for x, _ in blocks)
    max_y = max(y for _, y in blocks)
    cell_size = 20
    piece_html += (
        f"<div class='piece-grid' style='grid-template-columns: repeat({max_x+1}, {cell_size}px);"
        f" grid-template-rows: repeat({max_y+1}, {cell_size}px);'>"
    )
    for y in range(max_y+1):
        for x in range(max_x+1):
            if (x, y) in blocks:
                piece_html += f"<div style='width:{cell_size}px; height:{cell_size}px; background:{PIECE_COLORS_HTML[name]};'></div>"
            else:
                piece_html += f"<div style='width:{cell_size}px; height:{cell_size}px;'></div>"
    piece_html += "</div>"
piece_html += "</div>"
st.markdown(piece_html, unsafe_allow_html=True)

st.markdown("---")

# ----------------------
# Clickable Grid for Target
# ----------------------
st.markdown("<h3 class='section-title'>Select the Target Cell</h3>", unsafe_allow_html=True)
if "target" not in st.session_state:
    st.session_state["target"] = None

st.markdown(
    """
    <div class="target-wrapper">
        <p>Minimal grid, maximal clarity – the selected square turns bold immediately.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def set_target(cell_idx: int) -> None:
    """Update the selected target cell and rerun to refresh the grid immediately."""
    st.session_state["target"] = cell_idx
    # Buttons already trigger a rerun after callbacks; no explicit rerun needed.


grid_shell = st.columns([1, 4, 1])
with grid_shell[1]:
    for y in range(HEIGHT):
        row = st.columns(WIDTH, gap="small")
        for x in range(WIDTH):
            cell_idx = y * WIDTH + x
            is_selected = st.session_state["target"] == cell_idx
            label = "X" if is_selected else ""
            row[x].button(
                label,
                key=f"cell_{cell_idx}",
                use_container_width=True,
                on_click=set_target,
                args=(cell_idx,),
                type="primary" if is_selected else "secondary",
            )

target = st.session_state["target"]

if target is None:
    st.markdown(
        """
        <div class="target-hint">Tap any square to choose your target day.</div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

st.markdown("---")

# ----------------------
# Solve Puzzle
# ----------------------
with st.spinner("Solving..."):
    placements, solutions = solve(target)

st.markdown(f"### 🔎 Found {len(solutions)} solution(s)")

# ----------------------
# Render each solution centered, no gridlines
# ----------------------
def render_solution(sol):
    html = "<div style='display:inline-block; margin:12px;'>"
    html += "<div style='display:grid; grid-template-columns: repeat(%d, 30px); grid-template-rows: repeat(%d, 30px); gap:2px;'>" % (WIDTH, HEIGHT)
    for i in range(WIDTH*HEIGHT):
        if i == target:
            html += f"<div style='width:30px;height:30px;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:18px;'>X</div>"
            continue
        # Find which piece covers this cell
        color = "#ffffff"  # default empty
        for pid in sol:
            placement = placements[pid]
            if i in placement["cells"]:
                color = PIECE_COLORS_HTML[placement["piece"]]
                break
        html += f"<div style='width:30px;height:30px;background:{color};'></div>"
    html += "</div></div>"
    return html

# Center all solutions horizontally
solution_html = "<div style='text-align:center;'>"
for idx, sol in enumerate(solutions, 1):
    solution_html += f"<div style='margin-bottom:20px;'>"
    solution_html += f"<h4>Solution {idx}</h4>"
    solution_html += render_solution(sol)
    solution_html += "</div>"
solution_html += "</div>"

st.markdown(solution_html, unsafe_allow_html=True)
