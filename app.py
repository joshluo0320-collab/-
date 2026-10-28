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
@st.cache_data
def load_game_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    
    with open(os.path.join(data_dir, "generals.json"), "r", encoding="utf-8") as f:
        generals = {g["id"]: g for g in json.load(f)}
    with open(os.path.join(data_dir, "tactics.json"), "r", encoding="utf-8") as f:
        tactics = {t["id"]: t for t in json.load(f)}
    with open(os.path.join(data_dir, "equipments.json"), "r", encoding="utf-8") as f:
        equipments = {e["id"]: e for e in json.load(f)}
    with open(os.path.join(data_dir, "user_inventory.json"), "r", encoding="utf-8") as f:
        inventory = json.load(f)["inventory"]
        
    return generals, tactics, equipments, inventory

try:
    all_generals, all_tactics, all_equipments, user_inv = load_game_data()
except Exception as e:
    st.error(f"資料讀取失敗，請確認 data 資料夾下的 JSON 檔案格式與路徑正確。錯誤資訊: {e}")
    st.stop()

# ----------------- 運算核心輔助函式 -----------------
def calculate_stat_at_level(base, growth, level=50, rank=0, allocated=0):
    """計算 50 等屬性：基礎 + 成長*(50-1) + 紅度點數(紅度*10) + 自訂加點"""
    return base + growth * (level - 1) + (rank * 10) + allocated

def evaluate_team_diagnostics(team):
    """
    評估陣容的機制完整度、速度軸與衝突診斷
    """
    warnings = []
    synergies = []
    
    # 1. 速度軸排序 (由快到慢)
    speed_ranking = sorted(team, key=lambda x: x["final_speed"], reverse=True)
    
    # 2. 衝突檢測：陣法排他
    all_team_tactics = []
    for member in team:
        all_team_tactics.extend(member["tactics"])
        
    tactic_objs = [all_tactics[tid] for tid in all_team_tactics if tid]
    tactic_types = [t["type"] for t in tactic_objs]
    
    if tactic_types.count("Formation") > 1:
        warnings.append("⚠️ **陣法衝突**：隊伍中裝備了 2 個或以上的「陣法」，效果可能互相頂替或無法完全生效！")
        
    # 3. 陣營加成
    camps = set(member["general"]["camp"] for member in team)
    is_same_camp = len(camps) == 1
    if is_same_camp:
        synergies.append("✅ **同陣營協同**：觸發 10% 陣營全屬性科技加成。")
    else:
        warnings.append("ℹ️ **非全同陣營**：未啟動 10% 陣營屬性加成（若無三勢陣或特定劇本令，屬性上限略受影響）。")

    # 4. 特技連動檢測
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

    # 5. 五維指標評分 (0~100)
    score_burst = 50
    score_reduction = 40
    score_heal = 30
    score_control = 35
    score_purify = 20

    # 戰法效能權重疊加
    for tid in all_team_tactics:
        if not tid:
            continue
        if tid == "fu_ji_jun_min":
            score_reduction += 30
            score_heal += 15
        elif tid == "zan_bi_qi_feng":
            score_reduction += 35
        elif tid == "cao_chuan_jie_jian":
            score_purify += 40
            score_heal += 30
        elif tid == "gua_gu_liao_du":
            score_purify += 30
            score_heal += 35
        elif tid == "feng_shi_zhen":
            score_burst += 25
        elif tid == "dang_feng_cui_jue":
            score_control += 25
            score_burst += 15
        elif tid == "heng_sao_qian_jun":
            score_burst += 20
            score_control += 15
        elif tid == "shi_bie_san_ri":
            score_burst += 25
            score_reduction += 15

    if tian_gong_active:
        score_burst += 15
        score_control += 10
    if caita_active:
        score_control += 20

    # 邊界限幅
    radar_scores = {
        "輸出爆發": min(score_burst, 100),
        "前程減傷": min(score_reduction, 100),
        "續航治療": min(score_heal, 100),
        "控制能力": min(score_control, 100),
        "淨化解控": min(score_purify, 100)
    }

    # 輔助速序警告
    if len(speed_ranking) == 3:
        fastest = speed_ranking[0]
        if "cao_chuan_jie_jian" in all_team_tactics or "gua_gu_liao_du" in all_team_tactics:
            # 檢查解控戰法是否在一速手上
            has_cleanse = ("cao_chuan_jie_jian" in fastest["tactics"]) or ("gua_gu_liao_du" in fastest["tactics"])
            if not has_cleanse:
                warnings.append(f"💡 **配速提醒**：隊內最快出手為【{fastest['general']['name']}】({fastest['final_speed']:.1f})，若淨化/解控戰法由後手武將攜帶，可能無法在主力輸出動手前解除控制狀態。")

    return radar_scores, warnings, synergies, speed_ranking

# ----------------- 側邊欄：武將配置面板 -----------------
st.sidebar.title("⚔️ 隊伍配置面板")

def render_member_input(label_prefix, default_idx=0):
    st.sidebar.subheader(f"📌 {label_prefix}")
    gen_keys = list(all_generals.keys())
    selected_gen_id = st.sidebar.selectbox(
        f"選擇武將",
        options=gen_keys,
        format_func=lambda x: f"{all_generals[x]['name']} ({all_generals[x]['camp']})",
        index=default_idx,
        key=f"{label_prefix}_gen"
    )
    
    # 預設紅度比對個人卡池
    default_rank = 0
    for u_gen in user_inv["generals"]:
        if u_gen["general_id"] == selected_gen_id:
            default_rank = u_gen.get("rank", 0)
            break
            
    rank = st.sidebar.slider(f"紅度進階", 0, 5, default_rank, key=f"{label_prefix}_rank")
    
    tactic_options = ["(無)"] + list(all_tactics.keys())
    t1 = st.sidebar.selectbox(
        f"攜帶戰法 1",
        options=tactic_options,
        format_func=lambda x: all_tactics[x]["name"] if x in all_tactics else x,
        key=f"{label_prefix}_t1"
    )
    t2 = st.sidebar.selectbox(
        f"攜帶戰法 2",
        options=tactic_options,
        format_func=lambda x: all_tactics[x]["name"] if x in all_tactics else x,
        key=f"{label_prefix}_t2"
    )
    
    trait_options = ["(無)"] + list(all_equipments.keys())
    trait = st.sidebar.selectbox(
        f"裝備核心特技",
        options=trait_options,
        format_func=lambda x: all_equipments[x]["name"] if x in all_equipments else x,
        key=f"{label_prefix}_trait"
    )
    
    # 屬性運算
    gen_data = all_generals[selected_gen_id]
    final_spd = calculate_stat_at_level(
        gen_data["base_stats"]["speed"],
        gen_data["stat_growth"]["speed"],
        level=50,
        rank=rank
    )
    final_int = calculate_stat_at_level(
        gen_data["base_stats"]["intelligence"],
        gen_data["stat_growth"]["intelligence"],
        level=50,
        rank=rank
    )
    final_cmd = calculate_stat_at_level(
        gen_data["base_stats"]["command"],
        gen_data["stat_growth"]["command"],
        level=50,
        rank=rank
    )
    final_atk = calculate_stat_at_level(
        gen_data["base_stats"]["force"],
        gen_data["stat_growth"]["force"],
        level=50,
        rank=rank
    )
    
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

main_general = render_member_input("主將", default_idx=0)
sub_general_1 = render_member_input("副將一", default_idx=1 if len(all_generals) > 1 else 0)
sub_general_2 = render_member_input("副將二", default_idx=2 if len(all_generals) > 2 else 0)

current_team = [main_general, sub_general_1, sub_general_2]

# ----------------- 主介面展示 -----------------
st.title("🛡️ 三國志·戰略版 隊伍體檢報告")
st.markdown("針對武將基礎體質、紅度、攜帶戰法機制與特技進行全維度即時演算。")

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
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
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
            "陣營": m["general"]["camp"],
            "紅度": f"{m['rank']} 紅",
            "估計速度 (局外)": round(m["final_speed"], 1),
            "裝備特技": all_equipments[m["trait"]]["name"] if m["trait"] else "無"
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
        st.markdown(f"### {roles[idx]}：{g['name']}")
        st.caption(f"陣營: {g['camp']} | Cost: {g['cost']} | 進階: {member['rank']} 紅")
        
        # 戰法清單
        t_names = [all_tactics[t]["name"] for t in member["tactics"]]
        st.markdown(f"**自帶戰法**：`{g['innate_tactic_id']}`")
        st.markdown(f"**攜帶戰法**：{', '.join(t_names) if t_names else '未攜帶'}")
        
        # 特技
        trait_name = all_equipments[member["trait"]]["name"] if member["trait"] else "無"
        st.markdown(f"**核心特技**：`{trait_name}`")
        
        # 四維屬性面板
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
