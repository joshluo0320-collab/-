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
        "前程減傷": min(score_reduction, 100
