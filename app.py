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
    
    speed_ranking = sorted(team, key=lambda x: x["final_speed"], reverse=True)
    
    all_team_tactics = []
    for member in team:
        all_team_tactics.extend(member["tactics"])
        
    tactic_objs = [all_tactics[tid] for tid in all_team_tactics if tid]
    tactic_types = [t["type"] for t in tactic_objs]
    
    if tactic_types.count("Formation") > 1:
        warnings.append("⚠️ **陣法衝突**：隊伍中裝備了 2 個或以上的「陣法」，效果可能互相頂替或無法完全生效！")
        
    camps = set(member["general"]["camp"] for member in team)
    if len(camps) == 1:
        synergies.append("✅ **同陣營協同**：觸發 10% 陣營全屬性科技加成。")
    else:
        warnings.append("ℹ️ **非全同陣營**：未啟動 10% 陣營屬性加成（若無三勢陣或特定劇本令，屬性上限略受影響）。")

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

    score_burst = 50
    score_reduction = 40
    score_heal = 30
    score_control = 35
    score_purify = 20

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

    radar_scores = {
        "輸出爆發": min(score_burst, 100),
        "前程減傷": min(score_reduction, 100),
        "續航治療": min(score_heal, 100),
        "控制能力": min(score_control, 100),
        "淨化解控": min(score_purify, 100)
    }

    if len(speed_ranking) == 3:
        fastest = speed_ranking[0]
        if "cao_chuan_jie_jian" in all_team_tactics or "gua_gu_liao_du" in all_team_tactics:
            has_cleanse = ("cao_chuan_jie_jian" in fastest["tactics"]) or ("gua_gu_liao_du" in fastest["tactics"])
            if not has_cleanse:
                warnings.append(f"💡 **配速提醒**：隊內一速為【{fastest['general']['name']}】({fastest['final_speed']:.1f})，解控戰法若在慢速武將身上，可能無法在主力動手前解除控制。")

    return radar_scores, warnings, synergies, speed_ranking

# ----------------- 側邊欄：隊伍配置面板 -----------------
st.sidebar.title("⚔️ 隊伍配置面板")

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
    gen_keys = list(all_generals.keys())
    actual_idx = default_idx if default_idx < len(gen_keys) else 0
    selected_gen_id = st.sidebar.selectbox(
        f"選擇武將",
        options=gen_keys,
        format_func=lambda x: f"{all_generals[x]['name']} ({all_generals[x]['camp']})",
        index=actual_idx,
        key=f"{role_key}_gen"
    )
    
    default_rank = 0
    for u_gen in user_inv["generals"]:
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
    
    def get_available_tactics(current_key):
        used_tactics = set()
        for r, ts in slot_keys:
            key_name = f"{r}_{ts}"
            if key_name != current_key:
                val = st.session_state.get(key_name, "(無)")
                if val != "(無)":
                    used_tactics.add(val)
        
        all_t_keys = list(all_tactics.keys())
        available = ["(無)"] + [t for t in all_t_keys if t not in used_tactics]
        return available

    k1 = f"{role_key}_t1"
    avail_1 = get_available_tactics(k1)
    idx_1 = avail_1.index(st.session_state[k1]) if st.session_state[k1] in avail_1 else 0
    t1 = st.sidebar.selectbox(
        f"攜帶戰法 1",
        options=avail_1,
        index=idx_1,
        format_func=lambda x: all_tactics[x]["name"] if x in all_tactics else x,
        key=k1
    )
    
    k2 = f"{role_key}_t2"
    avail_2 = get_available_tactics(k2)
    idx_2 = avail_2.index(st.session_state[k2]) if st.session_state[k2] in avail_2 else 0
    t2 = st.sidebar.selectbox(
        f"攜帶戰法 2",
        options=avail_2,
        index=idx_2,
        format_func=lambda x: all_tactics[x]["name"] if x in all_tactics else x,
        key=k2
    )
    
    trait_options = ["(無)"] + list(all_equipments.keys())
    trait = st.sidebar.selectbox(
        f"裝備核心特技",
        options=trait_options,
        format_func=lambda x: all_equipments[x]["name"] if x in all_equipments else x,
        key=f"{role_key}_trait"
    )
    
    gen_data = all_generals[selected_gen_id]
    final_spd = calculate_stat_at_level(gen_data["base_stats"]["speed"], gen_data["stat_growth"]["speed"], rank=rank)
    final_int = calculate_stat_at_level(gen_data["base_stats"]["intelligence"], gen_data["stat_growth"]["intelligence"], rank=rank)
    final_cmd = calculate_stat_at_level(gen_data["base_stats"]["command"], gen_data["stat_growth"]["command"], rank=rank)
    final_atk = calculate_stat_at_level(gen_data["base_stats"]["force"], gen_data["stat_growth"]["force"], rank=rank)
    
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
st.markdown("針對武將基礎體質、進階等級（0~6 紅/動態）、戰法機制與特技進行全維度即時演算。")

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
            "陣營": m["general"]["camp"],
            "進階等級": f"{m['rank']} 紅" + (" (動態)" if m["rank"] == 6 else ""),
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
        rank_str = f"{member['rank']} 紅" + (" (含動態加點)" if member['rank'] == 6 else "")
        st.markdown(f"### {roles[idx]}：{g['name']}")
        st.caption(f"陣營: {g['camp']} | Cost: {g['cost']} | 進階: {rank_str}")
        
        t_names = [all_tactics[t]["name"] for t in member["tactics"]]
        st.markdown(f"**自帶戰法**：`{g['innate_tactic_id']}`")
        st.markdown(f"**攜帶戰法**：{', '.join(t_names) if t_names else '未攜帶'}")
        
        trait_name = all_equipments[member["trait"]]["name"] if member["trait"] else "無"
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

# ----------------- 新增功能：網頁端錄入新武將 -----------------
st.markdown("---")
with st.expander("➕ 快速新增武將至資料庫 (免手動修改 JSON)"):
    st.markdown("在此輸入新武將數值與自帶戰法，點擊送出後將直接寫入系統資料庫並自動重新整理。")
    
    with st.form("add_general_form", clear_on_submit=True):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            g_id = st.text_input("武將唯一 ID (英數底線，例如 jiang_wei)", placeholder="jiang_wei").strip()
            g_name = st.text_input("武將名稱", placeholder="姜維").strip()
            g_camp = st.selectbox("陣營", options=["WEI", "SHU", "WU", "QUN"], index=1)
            g_cost = st.number_input("統御值 (Cost)", min_value=3, max_value=7, value=7)
            
        with f_col2:
            st.markdown("**基礎屬性 (1等)**")
            f_atk = st.number_input("基礎武力", value=80.0, step=1.0)
            f_int = st.number_input("基礎智力", value=85.0, step=1.0)
            f_cmd = st.number_input("基礎統率", value=80.0, step=1.0)
            f_spd = st.number_input("基礎速度", value=60.0, step=1.0)
            
        with f_col3:
            st.markdown("**屬性成長率**")
            g_atk = st.number_input("武力成長", value=1.80, step=0.01)
            g_int = st.number_input("智力成長", value=2.00, step=0.01)
            g_cmd = st.number_input("統率成長", value=1.70, step=0.01)
            g_spd = st.number_input("速度成長", value=1.00, step=0.01)

        st.markdown("**兵種適性**")
        apt_c1, apt_c2, apt_c3, apt_c4 = st.columns(4)
        with apt_c1:
            apt_cav = st.selectbox("騎兵適性", options=["S", "A", "B", "C"], index=0)
        with apt_c2:
            apt_shi = st.selectbox("盾兵適性", options=["S", "A", "B", "C"], index=1)
        with apt_c3:
            apt_bow = st.selectbox("弓兵適性", options=["S", "A", "B", "C"], index=0)
        with apt_c4:
            apt_spe = st.selectbox("槍兵適性", options=["S", "A", "B", "C"], index=2)

        st.markdown("**自帶戰法資訊**")
        sf_col1, sf_col2 = st.columns(2)
        with sf_col1:
            t_name = st.text_input("自帶戰法名稱 (例如 義膽雄心)", placeholder="義膽雄心").strip()
        with sf_col2:
            t_type = st.selectbox("自帶戰法類型", options=["Passive", "Command", "Active", "Assault"], index=1)

        submitted = st.form_submit_button("💾 新增武將並儲存至資料庫")
        
        if submitted:
            if not g_id or not g_name:
                st.error("請填寫武將 ID 與武將名稱！")
            elif g_id in all_generals:
                st.error(f"武將 ID '{g_id}' 已經存在！請使用其他 ID。")
            else:
                new_gen_obj = {
                    "id": g_id,
                    "name": g_name,
                    "camp": g_camp,
                    "gender": "Male",
                    "cost": int(g_cost),
                    "base_aptitude": {
                        "Cavalry": apt_cav,
                        "Shield": apt_shi,
                        "Bow": apt_bow,
                        "Spear": apt_spe
                    },
                    "base_stats": {
                        "force": float(f_atk),
                        "intelligence": float(f_int),
                        "command": float(f_cmd),
                        "speed": float(f_spd)
                    },
                    "stat_growth": {
                        "force": float(g_atk),
                        "intelligence": float(g_int),
                        "command": float(g_cmd),
                        "speed": float(g_spd)
                    },
                    "innate_tactic_id": t_name if t_name else "自帶戰法",
                    "innate_tactic_type": t_type,
                    "tags": {
                        "role": ["Balanced"],
                        "stat_scaling": ["intelligence", "force"]
                    }
                }
                
                paths = get_data_paths()
                try:
                    # 讀取現有資料並追加
                    with open(paths["generals"], "r", encoding="utf-8") as f:
                        cur_list = json.load(f)
                    cur_list.append(new_gen_obj)
                    with open(paths["generals"], "w", encoding="utf-8") as f:
                        json.dump(cur_list, f, ensure_ascii=False, indent=2)
                        
                    # 同步加入個人卡池 (預設 0 紅)
                    with open(paths["inventory"], "r", encoding="utf-8") as f:
                        inv_data = json.load(f)
                    inv_data["inventory"]["generals"].append({
                        "general_id": g_id,
                        "rank": 0,
                        "level": 50,
                        "treasures": [],
                        "is_locked": False
                    })
                    with open(paths["inventory"], "w", encoding="utf-8") as f:
                        json.dump(inv_data, f, ensure_ascii=False, indent=2)

                    st.cache_data.clear()
                    st.success(f"🎉 成功新增武將【{g_name}】！頁面將自動重新整理。")
                    st.rerun()
st.markdown("---")
if st.button("🔄 一鍵同步/重構【全五星武將庫 + 全 S 級戰法庫】"):
    import sync_full_db
    sync_full_db.generate_full_database()
    st.cache_data.clear()
    st.success("🎉 全武將與全 S 級戰法庫已同步完成！請重新整理頁面。")
    st.rerun()
                
                except Exception as write_err:
                    st.warning(f"本地檔案寫入失敗 ({write_err})。請複製以下 JSON 片段手動貼回 GitHub 的 data/generals.json：")
                    st.code(json.dumps(new_gen_obj, ensure_ascii=False, indent=2), language="json")
