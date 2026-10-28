import json
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ----------------- 頁面基礎設定 -----------------
st.set_page_config(
    page_title="三國志戰略版 - 陣容體檢與評測系統",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- 資料讀取模組 -----------------
def get_data_paths():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    return {
        "generals": os.path.join(data_dir, "generals.json"),
        "tactics": os.path.join(data_dir, "tactics.json"),
        "equipments": os.path.join(data_dir, "equipments.json"),
        "inventory": os.path.join(data_dir, "user_inventory.json")
    }

@st.cache_data
def load_game_data():
    paths = get_data_paths()
    with open(paths["generals"], "r", encoding="utf-8") as f:
        generals = {g["id"]: g for g in json.load(f)}
    with open(paths["tactics"], "r", encoding="utf-8") as f:
        tactics = {t["id"]: t for t in json.load(f)}
    with open(paths["equipments"], "r", encoding="utf-8") as f:
        equipments = {e["id"]: e for e in json.load(f)}
    with open(paths["inventory"], "r", encoding="utf-8") as f:
        inventory = json.load(f)["inventory"]
        
    return generals, tactics, equipments, inventory

try:
    all_generals, all_tactics, all_equipments, user_inv = load_game_data()
except Exception as e:
    st.error(f"資料讀取失敗，請確認 data 資料夾下的 JSON 檔案格式與路徑正確。錯誤: {e}")
    st.stop()

# ----------------- 運算核心輔助函式 -----------------
def calculate_stat_at_level(base, growth, level=50, rank=0, allocated=0):
    """計算 50 等屬性：基礎 + 成長*(50-1) + 紅度點數(紅度*10，含動態) + 自訂加點"""
    return base + growth * (level - 1) + (rank * 10) + allocated

def evaluate_team_diagnostics(team):
    warnings = []
    synergies = []
    
    # 速度軸排序
    speed_ranking = sorted(team, key=lambda x: x["final_speed"], reverse=True)
    
    # 陣法衝突檢測
    all_team_tactics = []
    for member in team:
        all_team_tactics.extend(member["tactics"])
        
    tactic_objs = [all_tactics[tid] for tid in all_team_tactics if tid in all_tactics]
    tactic_types = [t.get("type") for t in tactic_objs]
    
    if tactic_types.count("Formation") > 1:
        warnings.append("⚠️ **陣法衝突**：隊伍中裝備了 2 個或以上的「陣法」，效果可能互相頂替或無法完全生效！")
        
    # 兵種衝突檢測
    if tactic_types.count("Troop") > 1:
        warnings.append("⚠️ **兵種衝突**：隊伍中裝備了 2 個或以上的「特定兵種」，無法同時生效！")

    # 陣營協同檢測
    camps = set(member["general"]["camp"] for member in team)
    if len(camps) == 1:
        synergies.append("✅ **同陣營協同**：觸發 10% 陣營全屬性科技加成。")
    else:
        warnings.append("ℹ️ **非全同陣營**：未啟動 10% 陣營屬性加成（若無三勢陣或特定劇本令，屬性上限略受影響）。")

    # 特技連動
    tian_gong_active = False
    caita_active = False
    for member in team:
        gid = member["general"]["id"]
        trait = member["trait"]
        if gid == "zhang_jiao" and trait == "trait_tian_gong":
            tian_gong_active = True
            synergies.append("⚡ **天公質變**：張角裝備專屬天公特技，大幅提升五雷轟頂震懾與傷害段數。")
        if gid == "guan_yinping" and trait == "trait_cai_ta":
            caita_active = True
            synergies.append("🐎 **踩踏連動**：關銀屏配置踩踏特技，普攻附帶兵刃打擊，加速虎嗔震懾觸發。")

    # 五維評分系統 (以動態權重與標籤驅動)
    score_burst = 45
    score_reduction = 35
    score_heal = 25
    score_control = 30
    score_purify = 15

    for tid in all_team_tactics:
        if not tid or tid not in all_tactics:
            continue
        t_obj = all_tactics[tid]
        t_tags = t_obj.get("tags", {}).get("category", [])
        
        # 標籤化加權
        if "S_Tier_Defense" in t_tags:
            score_reduction += 30
        if "Pre_Round_Reduction" in t_tags:
            score_reduction += 25
        if "Purify" in t_tags or "Targeted_Purify" in t_tags:
            score_purify += 35
        if "Recovery" in t_tags or "Emergency_Recovery" in t_tags:
            score_heal += 25
        if "Single_Core_Amplifier" in t_tags or "Mixed_Camp_Amplifier" in t_tags:
            score_burst += 20
        if "Core_Breaker" in t_tags or "Pseudo_Report" in t_tags:
            score_control += 25
        if "Disarm" in t_tags or "Stun" in t_tags or "Weakness" in t_tags:
            score_control += 25
        if "AOE_Damage" in t_tags or "Turn4_Burst" in t_tags or "Mage_Crit" in t_tags:
            score_burst += 20

    if tian_gong_active:
        score_burst += 15
        score_control += 10
    if caita_active:
        score_control += 20

    radar_scores = {
        "輸出爆發": min(score_burst, 100),
        "前程減傷": min(score_reduction, 100),
        "續航治療": min(score_heal, 100),
        "控制能力": min(score_control, 100),
        "淨化解控": min(score_purify, 100)
    }

    # 配速提醒
    if len(speed_ranking) == 3:
        fastest = speed_ranking[0]
        if "cao_chuan_jie_jian" in all_team_tactics or "gua_gu_liao_du" in all_team_tactics:
            has_cleanse = ("cao_chuan_jie_jian" in fastest["tactics"]) or ("gua_gu_liao_du" in fastest["tactics"])
            if not has_cleanse:
                warnings.append(f"💡 **配速提醒**：隊內一速為【{fastest['general']['name']}】({fastest['final_speed']:.1f})，解控戰法若在慢速武將身上，可能無法在主力動手前解除控制。")

    return radar_scores, warnings, synergies, speed_ranking

# ----------------- 側邊欄：隊伍配置面板 -----------------
st.sidebar.title("⚔️ 隊伍配置面板")

# 陣營與戰法品質全域篩選器（解決全量庫下拉選單過長問題）
with st.sidebar.expander("🔍 快速篩選設定", expanded=False):
    camp_filter = st.selectbox("武將陣營篩選", ["全部", "WEI", "SHU", "WU", "QUN"], index=0)
    grade_filter = st.radio("戰法品質篩選", ["全部", "S", "A"], horizontal=True, index=0)

# 初始化 session_state
slot_keys = [
    ("main", "t1"), ("main", "t2"),
    ("sub1", "t1"), ("sub1", "t2"),
    ("sub2", "t1"), ("sub2", "t2")
]
for role, t_slot in slot_keys:
    k = f"{role}_{t_slot}"
    if k not in st.session_state:
        st.session_state[k] = "(無)"

def render_member_input(role_key, role_label, default_idx=0):
    st.sidebar.subheader(f"📌 {role_label}")
    
    # 武將陣營過濾
    if camp_filter == "全部":
        filtered_gen_keys = list(all_generals.keys())
    else:
        filtered_gen_keys = [gid for gid, g in all_generals.items() if g.get("camp") == camp_filter]
        
    if not filtered_gen_keys:
        filtered_gen_keys = list(all_generals.keys())
        
    actual_idx = default_idx if default_idx < len(filtered_gen_keys) else 0
    selected_gen_id = st.sidebar.selectbox(
        f"選擇武將",
        options=filtered_gen_keys,
        format_func=lambda x: f"{all_generals[x]['name']} ({all_generals[x].get('camp', '')})",
        index=actual_idx,
        key=f"{role_key}_gen"
    )
    
    # 預設紅度比對個人卡池
    default_rank = 0
    for u_gen in user_inv.get("generals", []):
        if u_gen["general_id"] == selected_gen_id:
            default_rank = min(u_gen.get("rank", 0), 6)
            break
            
    rank = st.sidebar.slider(
        f"進階等級 (紅度/動態)",
        min_value=0,
        max_value=6,
        value=default_rank,
        help="0~5 為標準進階紅度；6 代表滿紅並解鎖「動態武將」（額外獲得 10 點屬性）。",
        key=f"{role_key}_rank"
    )
    
    # 戰法動態排他過濾 + 品質篩選
    def get_available_tactics(current_key):
        used_tactics = set()
        for r, ts in slot_keys:
            key_name = f"{r}_{ts}"
            if key_name != current_key:
                val = st.session_state.get(key_name, "(無)")
                if val != "(無)":
                    used_tactics.add(val)
        
        # 根據品質過濾
        candidate_tactics = []
        for tid, t_obj in all_tactics.items():
            if grade_filter == "全部" or t_obj.get("grade") == grade_filter:
                candidate_tactics.append(tid)
                
        available = ["(無)"] + [t for t in candidate_tactics if t not in used_tactics]
        return available

    k1 = f"{role_key}_t1"
    avail_1 = get_available_tactics(k1)
    idx_1 = avail_1.index(st.session_state[k1]) if st.session_state[k1] in avail_1 else 0
    t1 = st.sidebar.selectbox(
        f"攜帶戰法 1",
        options=avail_1,
        index=idx_1,
        format_func=lambda x: f"[{all_tactics[x].get('grade','S')}] {all_tactics[x]['name']}" if x in all_tactics else x,
        key=k1
    )
    
    k2 = f"{role_key}_t2"
    avail_2 = get_available_tactics(k2)
    idx_2 = avail_2.index(st.session_state[k2]) if st.session_state[k2] in avail_2 else 0
    t2 = st.sidebar.selectbox(
        f"攜帶戰法 2",
        options=avail_2,
        index=idx_2,
        format_func=lambda x: f"[{all_tactics[x].get('grade','S')}] {all_tactics[x]['name']}" if x in all_tactics else x,
        key=k2
    )
    
    # 裝備特技選取
    trait_options = ["(無)"] + list(all_equipments.keys())
    trait = st.sidebar.selectbox(
        f"裝備核心特技",
        options=trait_options,
        format_func=lambda x: all_equipments[x]["name"] if x in all_equipments else x,
        key=f"{role_key}_trait"
    )
    
    gen_data = all_generals[selected_gen_id]
    b_stats = gen_data.get("base_stats", {"speed": 50, "intelligence": 50, "command": 50, "force": 50})
    s_growths = gen_data.get("stat_growth", {"speed": 1.0, "intelligence": 1.0, "command": 1.0, "force": 1.0})
    
    final_spd = calculate_stat_at_level(b_stats.get("speed", 50), s_growths.get("speed", 1.0), rank=rank)
    final_int = calculate_stat_at_level(b_stats.get("intelligence", 50), s_growths.get("intelligence", 1.0), rank=rank)
    final_cmd = calculate_stat_at_level(b_stats.get("command", 50), s_growths.get("command", 1.0), rank=rank)
    final_atk = calculate_stat_at_level(b_stats.get("force", 50), s_growths.get("force", 1.0), rank=rank)
    
    return {
        "general": gen_data,
        "rank": rank,
        "tactics": [t for t in [t1, t2] if t != "(無)"],
        "trait": trait if trait != "(無)" else None,
        "final_speed": final_spd,
        "final_intelligence": final_int,
        "final_command": final_cmd,
        "final_attack": final_atk
    }

main_general = render_member_input("main", "主將", default_idx=0)
sub_general_1 = render_member_input("sub1", "副將一", default_idx=1 if len(all_generals) > 1 else 0)
sub_general_2 = render_member_input("sub2", "副將二", default_idx=2 if len(all_generals) > 2 else 0)

current_team = [main_general, sub_general_1, sub_general_2]

# ----------------- 主介面展示 -----------------
st.title("🛡️ 三國志·戰略版 隊伍體檢報告")
st.caption(f"目前資料庫狀態：已收錄 {len(all_generals)} 位武將 | {len(all_tactics)} 個戰法 | {len(all_equipments)} 件特技裝備")

radar_scores, warnings, synergies, speed_ranking = evaluate_team_diagnostics(current_team)

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📊 隊伍機制五維雷達")
    categories = list(radar_scores.keys())
    values = list(radar_scores.values())
    categories.append(categories[0])
    values.append(values[0])
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(230, 81, 0, 0.3)',
        line=dict(color='#E65100', width=2),
        name='體檢分數'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=380,
        margin=dict(l=40, r=40, t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("⏱️ 速度軸出手順序 (50等實裝估計)")
    spd_df = pd.DataFrame([
        {
            "武將": m["general"]["name"],
            "陣營": m["general"].get("camp", ""),
            "進階等級": f"{m['rank']} 紅" + (" (動態)" if m["rank"] == 6 else ""),
            "估計速度 (局外)": round(m["final_speed"], 1),
            "裝備特技": all_equipments[m["trait"]]["name"] if m["trait"] in all_equipments else "無"
        }
        for m in speed_ranking
    ])
    st.dataframe(spd_df, use_container_width=True, hide_index=True)
    
    st.subheader("🩺 機制診斷與建議")
    if synergies:
        for syn in synergies:
            st.success(syn)
    if warnings:
        for w in warnings:
            st.warning(w)

st.markdown("---")
st.subheader("📋 陣容總覽與 50 等屬性面板")

cols = st.columns(3)
roles = ["主將", "副將一", "副將二"]

for idx, (col, member) in enumerate(zip(cols, current_team)):
    g = member["general"]
    with col:
        rank_str = f"{member['rank']} 紅" + (" (含動態加點)" if member['rank'] == 6 else "")
        st.markdown(f"### {roles[idx]}：{g['name']}")
        st.caption(f"陣營: {g.get('camp', '')} | Cost: {g.get('cost', '')} | 進階: {rank_str}")
        
        t_names = [all_tactics[t]["name"] for t in member["tactics"] if t in all_tactics]
        st.markdown(f"**自帶戰法**：`{g.get('innate_tactic_id', '自帶戰法')}`")
        st.markdown(f"**攜帶戰法**：{', '.join(t_names) if t_names else '未攜帶'}")
        
        trait_name = all_equipments[member["trait"]]["name"] if member["trait"] in all_equipments else "無"
        st.markdown(f"**核心特技**：`{trait_name}`")
        
        stat_data = {
            "屬性": ["武力", "智力", "統率", "速度"],
            "面板估值": [
                round(member["final_attack"], 1),
                round(member["final_intelligence"], 1),
                round(member["final_command"], 1),
                round(member["final_speed"], 1)
            ]
        }
        st.table(pd.DataFrame(stat_data))

# ----------------- 底部：全自動資料庫同步面板 -----------------
st.markdown("---")
st.subheader("⚙️ 全資料庫自動維護")
st.markdown("如果你的資料庫尚未包含全部五星橙將與全 S/A 戰法，可點擊下方按鈕直接連線抓取並自動更新檔案：")

if st.button("🚀 執行 sync_full_db.py（抓取並重構全橙將與全 S/A 戰法庫）"):
    with st.spinner("正在連線下載並寫入全量資料庫，請稍候約 5~10 秒..."):
        try:
            import sync_full_db
            sync_full_db.fetch_and_build_complete_database()
            st.cache_data.clear()
            st.success("🎉 全武將庫與全戰法庫已全數同步！正在自動重新載入頁面...")
            st.rerun()
        except Exception as sync_err:
            st.error(f"同步過程中發生錯誤: {sync_err}")
