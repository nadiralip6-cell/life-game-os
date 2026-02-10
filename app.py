import streamlit as st
import random
import json
import os
import time

# ==========================================
# 1. UI 配置 (Obsidian Theme)
# ==========================================
st.set_page_config(page_title="LifeGame V17", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* 背景：极黑 */
    [data-testid="stAppViewContainer"] {
        background-color: #000000;
        background-image: radial-gradient(circle at 50% 0%, #111 0%, #000 80%);
        color: #e0e0e0;
    }
    
    [data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 1px solid #222;
    }

    h1, h2, h3 { color: #fff !important; font-weight: 900 !important; }
    p, label { color: #888 !important; }

    /* 按钮 */
    div.stButton > button {
        background-color: #0A0A0A;
        color: #fff;
        border: 1px solid #333;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background-color: #fff;
        color: #000;
        border-color: #fff;
    }

    /* 输入框 */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #111 !important;
        color: #fff !important;
        border: 1px solid #333 !important;
        border-radius: 8px;
    }

    /* 进度条底槽 & 填充 */
    div[data-testid="stProgress"] > div > div {
        background-color: #333333 !important;
        height: 8px !important;
        border-radius: 10px;
    }
    div[data-testid="stProgress"] > div > div > div > div {
        background-color: #ffffff !important;
        border-radius: 10px;
    }

    /* 徽章卡片 */
    .badge-card {
        background: #111;
        border: 1px solid #222;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        text-align: center;
    }
    .rank-bronze { border-color: #cd7f32; color: #cd7f32; }
    .rank-silver { border-color: #ccc; color: #ccc; }
    .rank-gold { border-color: #FFD700; color: #FFD700; }
    .rank-diamond { border-color: #00e5ff; color: #00e5ff; }
    .rank-king { border-color: #e040fb; color: #e040fb; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { border-bottom: 1px solid #222; }
    .stTabs [data-baseweb="tab"] { color: #666; }
    .stTabs [aria-selected="true"] { color: #fff !important; border-bottom: 2px solid #fff; }

    /* 排行榜样式 */
    .leader-row {
        padding: 10px;
        border-bottom: 1px solid #222;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .rank-1 { color: #FFD700; font-weight: bold; font-size: 1.1em; border: 1px solid #FFD700; border-radius: 8px; padding: 5px 10px; box-shadow: 0 0 10px rgba(255, 215, 0, 0.2); }
    .rank-2 { color: #C0C0C0; font-weight: bold; font-size: 1.1em; }
    .rank-3 { color: #CD7F32; font-weight: bold; font-size: 1.1em; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 存档与排行榜系统
# ==========================================

def get_save_file(username):
    safe_name = "".join([c for c in username if c.isalnum()])
    if not safe_name: safe_name = "guest"
    return f"save_{safe_name}.json"

def load_data(username):
    file_path = get_save_file(username)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def save_data(username):
    file_path = get_save_file(username)
    data = {
        "xp": st.session_state.xp,
        "level": st.session_state.level,
        "energy": st.session_state.energy,
        "gold": st.session_state.gold,
        "count_gym": st.session_state.count_gym,
        "count_focus": st.session_state.count_focus,
        "count_review": st.session_state.count_review,
        "activities": st.session_state.activities,
        "rewards": st.session_state.rewards
    }
    with open(file_path, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_leaderboard_data():
    files = [f for f in os.listdir('.') if f.startswith('save_') and f.endswith('.json')]
    leaderboard = []
    for f in files:
        try:
            user_name = f.replace("save_", "").replace(".json", "")
            with open(f, "r", encoding='utf-8') as file:
                data = json.load(file)
                lvl = data.get('level', 1)
                xp = data.get('xp', 0)
                score = (lvl * 100) + xp 
                leaderboard.append({"name": user_name, "level": lvl, "score": score})
        except: continue
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    return leaderboard

# ==========================================
# 3. 核心工具函数
# ==========================================
def render_custom_bar(label, value, max_val, color_start, color_end):
    percentage = min(100, max(0, (value / max_val) * 100))
    bar_html = f"""
    <div style="margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 14px; font-weight: 600; color: #ccc;">
            <span>{label}</span>
            <span>{int(value)} / {max_val}</span>
        </div>
        <div style="width: 100%; background-color: #222; border-radius: 6px; height: 10px; border: 1px solid #333;">
            <div style="width: {percentage}%; background: linear-gradient(90deg, {color_start}, {color_end}); height: 100%; border-radius: 6px; transition: width 0.4s ease;"></div>
        </div>
    </div>
    """
    st.markdown(bar_html, unsafe_allow_html=True)

def get_badge_status(count, name_map):
    tiers = [
        (120, "👑", "rank-king", "KING"),
        (90, "💎", "rank-diamond", "DIAMOND"),
        (50, "🥇", "rank-gold", "GOLD"),
        (21, "🥈", "rank-silver", "SILVER"),
        (7, "🥉", "rank-bronze", "BRONZE"),
    ]
    for threshold, icon, style, rank_name in tiers:
        if count >= threshold:
            return f"<div class='badge-card {style}'>{icon} {name_map}<br><b>{rank_name}</b><br><small>{count}</small></div>"
    return f"<div class='badge-card' style='border-style:dashed; color:#444;'>🔒 {name_map}<br><small>{count}/7</small></div>"

# ==========================================
# 4. 侧边栏：完整控制台
# ==========================================
with st.sidebar:
    st.title("CMD CENTER")
    
    st.markdown("### 🆔 PLAYER ID")
    user_id = st.text_input("Login Name", "Guest")
    
    if 'current_user' not in st.session_state: st.session_state.current_user = user_id
    
    saved_data = load_data(user_id)
    if st.session_state.current_user != user_id:
        st.session_state.current_user = user_id
        saved_data = load_data(user_id)
        for key in ['xp', 'level', 'energy', 'gold', 'activities', 'rewards']:
            if key in st.session_state: del st.session_state[key]

    # --- 数据填充 ---
    if saved_data:
        if 'xp' not in st.session_state: st.session_state.xp = saved_data.get('xp', 0.0)
        if 'level' not in st.session_state: st.session_state.level = saved_data.get('level', 1)
        if 'energy' not in st.session_state: st.session_state.energy = saved_data.get('energy', 100.0)
        if 'gold' not in st.session_state: st.session_state.gold = saved_data.get('gold', 0.0)
        if 'count_gym' not in st.session_state: st.session_state.count_gym = saved_data.get('count_gym', 0)
        if 'count_focus' not in st.session_state: st.session_state.count_focus = saved_data.get('count_focus', 0)
        if 'count_review' not in st.session_state: st.session_state.count_review = saved_data.get('count_review', 0)
        if 'activities' not in st.session_state: st.session_state.activities = saved_data.get('activities', {})
        if 'rewards' not in st.session_state: st.session_state.rewards = saved_data.get('rewards', {})
    else:
        if 'xp' not in st.session_state: st.session_state.xp = 0.0
        if 'level' not in st.session_state: st.session_state.level = 1
        if 'energy' not in st.session_state: st.session_state.energy = 100.0
        if 'gold' not in st.session_state: st.session_state.gold = 0.0
        if 'count_gym' not in st.session_state: st.session_state.count_gym = 0
        if 'count_focus' not in st.session_state: st.session_state.count_focus = 0
        if 'count_review' not in st.session_state: st.session_state.count_review = 0
        
        if 'activities' not in st.session_state or not st.session_state.activities:
            st.session_state.activities = {
                "🍳 营养早饭": [2.0, +15.0, "count", "Morning"],
                "🧼 洗碗家务": [1.0, -2.0, "count", "Morning"],
                "❄️ 寒冷启动": [5.0, +8.0, "count", "Morning"],
                "🔥 Focus Zone": [1.5, -0.6, "time", "Work"], 
                "🚬 抽根烟": [0.0, +3.0, "count", "Life"],
                "📱 划手机": [0.1, +0.2, "time", "Life"],
                "🚶‍♂️ 散步+饮料": [3.0, +10.0, "count", "Life"],
                "👨‍🍳 做饭": [5.0, -5.0, "count", "Life"],
                "📺 吃饭+老友记": [1.0, +15.0, "time", "Life"],
                "💪 健身房": [2.0, -1.0, "time", "Night"], 
                "📝 每日复盘": [10.0, -5.0, "count", "Night"],
                "🛌 睡觉": [0.0, +1.5, "time", "Night"],
            }
        if 'rewards' not in st.session_state or not st.session_state.rewards:
            st.session_state.rewards = {
                "🥤 奶茶": 600, "🎮 新游戏": 8000, "✈️ 旅行": 30000
            }

    # --- 1. 小金库 ---
    st.markdown(f"<div class='gold-stat'>{int(st.session_state.gold)}</div>", unsafe_allow_html=True)
    st.caption("GOLD RESERVES")
    
    if st.button("💾 SAVE DATA"):
        save_data(user_id)
        st.toast(f"Saved: {user_id}")

    # --- 2. 排行榜 (新功能) ---
    st.write("---")
    with st.expander("🏆 GLOBAL RANKING", expanded=True):
        leaders = get_leaderboard_data()
        if not leaders:
            st.caption("No data yet.")
        else:
            rank = 1
            for player in leaders:
                icon = f"#{rank}"
                style_class = ""
                if rank == 1: 
                    icon = "🥇"
                    style_class = "rank-1"
                elif rank == 2: 
                    icon = "🥈"
                    style_class = "rank-2"
                elif rank == 3: 
                    icon = "🥉"
                    style_class = "rank-3"
                is_me = "(ME)" if player['name'] == user_id else ""
                st.markdown(f"""
                <div class="leader-row">
                    <span class="{style_class}">{icon} {player['name']} {is_me}</span>
                    <span style="color:#888; font-family:monospace">LV.{player['level']}</span>
                </div>
                """, unsafe_allow_html=True)
                rank += 1
            if st.button("🔄 Refresh Rank"):
                st.rerun()

    # --- 3. 进化段位 (加回来了！) ---
    st.write("---")
    with st.expander("🎖️ EVOLUTION (RANKS)"):
        st.markdown(get_badge_status(st.session_state.count_gym, "STR (Strength)"), unsafe_allow_html=True)
        st.markdown(get_badge_status(st.session_state.count_focus, "INT (Intellect)"), unsafe_allow_html=True)
        st.markdown(get_badge_status(st.session_state.count_review, "WIS (Wisdom)"), unsafe_allow_html=True)

    # --- 4. 奖励兑换 (加回来了！) ---
    st.write("---")
    with st.expander("🎁 REWARDS (SHOP)"):
        for item, cost in st.session_state.rewards.items():
            if st.session_state.gold >= cost:
                if st.button(f"CLAIM {item}", key=f"r_{item}"):
                    st.balloons()
            else:
                st.button(f"{item} ({int(cost - st.session_state.gold)})", disabled=True, key=f"l_{item}")
    
    # --- 5. 添加新项目 ---
    st.write("---")
    with st.expander("➕ ADD NEW"):
        tab1, tab2 = st.tabs(["ACT", "REW"])
        with tab1:
            n_act = st.text_input("Name")
            cat = st.selectbox("Type", ["Morning", "Work", "Life", "Night"])
            mode = st.radio("Mode", ["⏳Time", "⚡Count"], horizontal=True)
            if st.button("Add Act"):
                m_code = "time" if "Time" in mode else "count"
                st.session_state.activities[n_act] = [1.0, 0.0, m_code, cat]
                save_data(user_id)
                st.rerun()
        with tab2:
            n_rew = st.text_input("Reward")
            n_cost = st.number_input("Cost", step=100, value=5000)
            if st.button("Add Rew"):
                st.session_state.rewards[n_rew] = n_cost
                save_data(user_id)
                st.rerun()

# ==========================================
# 5. 主逻辑
# ==========================================
while st.session_state.xp >= 100:
    st.session_state.level += 1
    st.session_state.xp -= 100
    st.toast(f"LEVEL UP! LV.{st.session_state.level}")
    save_data(user_id)

# ==========================================
# 6. 主界面
# ==========================================
c1, c2 = st.columns([3, 1])
with c1: st.title(f"LifeGame: {user_id}")
with c2: st.metric("LEVEL", f"{st.session_state.level}")

st.write("---")

c_xp, c_en = st.columns(2)
with c_xp:
    render_custom_bar("EXPERIENCE", st.session_state.xp, 100, "#FFD700", "#FDB931")
with c_en:
    render_custom_bar("ENERGY", st.session_state.energy, 100, "#00d2ff", "#3a7bd5")

st.markdown(f"<div class='gold-stat' style='text-align:center; margin-top:20px'>{int(st.session_state.gold)} <span style='font-size:0.4em; color:#666'>GOLD</span></div>", unsafe_allow_html=True)

# ==========================================
# 7. 行动区
# ==========================================
st.write("### 🗓️ Daily Protocol")

tab_m, tab_w, tab_l, tab_n = st.tabs(["MORNING", "FOCUS", "LIFE", "NIGHT"])
tabs_map = {"Morning": tab_m, "Work": tab_w, "Life": tab_l, "Night": tab_n}

for name, values in st.session_state.activities.items():
    if len(values) == 4:
        xp_u, en_u, mode, category = values
    elif len(values) == 3:
        xp_u, en_u, mode = values
        category = "Life"
    else: continue

    current_tab = tabs_map.get(category, tab_l)
    
    with current_tab:
        with st.container():
            c_info, c_input, c_btn = st.columns([2, 1, 1])
            with c_info:
                st.markdown(f"**{name}**")
                if en_u > 0:
                    badge_color = "#4ade80"
                    badge_text = "RECOVER"
                else:
                    badge_color = "#f87171"
                    badge_text = "DRAIN"
                unit_label = "min" if mode == "time" else "unit"
                st.markdown(f"<span style='color:#666; font-size:0.8em'>XP +{xp_u} · <span style='color:{badge_color}'>{badge_text} {abs(en_u)}</span> / {unit_label}</span>", unsafe_allow_html=True)
            
            with c_input:
                d_val = 60 if "Focus" in name else (30 if mode == "time" else 1)
                amount = st.number_input("Qty", 1, 600, d_val, key=f"in_{name}", label_visibility="collapsed")
            
            with c_btn:
                if st.button("DONE", key=f"do_{name}", use_container_width=True):
                    t_xp = amount * xp_u
                    t_en = amount * en_u
                    
                    is_crit = False
                    if random.random() < 0.1:
                        is_crit = True
                        t_xp = t_xp * 2

                    if t_en < 0 and st.session_state.energy + t_en < 0:
                        st.error("LOW ENERGY")
                    else:
                        st.session_state.xp += t_xp
                        st.session_state.gold += t_xp
                        st.session_state.energy += t_en
                        if st.session_state.energy > 100: st.session_state.energy = 100
                        
                        if "Focus" in name: st.session_state.count_focus += 1
                        if "复盘" in name: st.session_state.count_review += 1
                        if "健身" in name: st.session_state.count_gym += 1
                        
                        save_data(user_id) 
                        
                        if is_crit: st.toast(f"🔥 CRIT! XP +{int(t_xp)}")
                        else: st.toast(f"Done. XP +{int(t_xp)}")
                        time.sleep(0.5)
                        st.rerun()
        st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)