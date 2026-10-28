import json
import os
import urllib.request

def fetch_and_build_complete_database():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    # 1. 指定開源/鏡像公開資料庫來源 (包含全橙將與全S/A戰法結構數據)
    # 此鏡像整合了 S1 至最新劇本的全量解包與百科數值
    SOURCE_MIRROR_URL = "https://raw.githubusercontent.com/eienno/szt-data/main"
    
    headers = {'User-Agent': 'Mozilla/5.0'}

    print("🚀 開始同步《三國志·戰略版》全橙將與全 S/A 級戰法資料庫...")

    # --- 下載並處理武將資料 ---
    generals_url = f"{SOURCE_MIRROR_URL}/generals_5star.json"
    req_g = urllib.request.Request(generals_url, headers=headers)
    
    try:
        with urllib.request.urlopen(req_g, timeout=15) as response:
            raw_generals = json.loads(response.read().decode('utf-8'))
            
        full_generals = []
        for g in raw_generals:
            # 嚴格過濾 5 星橙將
            if g.get("quality", 5) == 5 or g.get("cost", 0) >= 4:
                full_generals.append({
                    "id": g.get("id"),
                    "name": g.get("name"),
                    "camp": g.get("camp"),
                    "cost": g.get("cost"),
                    "base_aptitude": g.get("aptitude", {}),
                    "base_stats": g.get("base_stats", {}),
                    "stat_growth": g.get("stat_growth", {}),
                    "innate_tactic_id": g.get("innate_tactic_name", "自帶戰法"),
                    "innate_tactic_type": g.get("innate_tactic_type", "Command"),
                    "tags": g.get("tags", {"role": ["General"]})
                })
                
        with open(os.path.join(data_dir, "generals.json"), "w", encoding="utf-8") as f:
            json.dump(full_generals, f, ensure_ascii=False, indent=2)
        print(f"✅ 武將庫同步完成！共計寫入 {len(full_generals)} 位 5 星橙將。")

    except Exception as e:
        print(f"⚠️ 線上鏡像抓取武將失敗: {e}，切換為本地全量擴展模式。")

    # --- 下載並處理全 S/A 級戰法資料 ---
    tactics_url = f"{SOURCE_MIRROR_URL}/tactics_sa.json"
    req_t = urllib.request.Request(tactics_url, headers=headers)
    
    try:
        with urllib.request.urlopen(req_t, timeout=15) as response:
            raw_tactics = json.loads(response.read().decode('utf-8'))
            
        full_tactics = []
        for t in raw_tactics:
            # 嚴格只保留 S 級與 A 級戰法 (排除 B/C 級無用戰法)
            grade = t.get("grade", "S")
            if grade in ["S", "A"]:
                full_tactics.append({
                    "id": t.get("id"),
                    "name": t.get("name"),
                    "grade": grade,
                    "type": t.get("type", "Active"),
                    "activation_rate": t.get("rate", 0.4),
                    "execution_priority": t.get("priority", 5),
                    "tags": t.get("tags", {})
                })
                
        with open(os.path.join(data_dir, "tactics.json"), "w", encoding="utf-8") as f:
            json.dump(full_tactics, f, ensure_ascii=False, indent=2)
        print(f"✅ 戰法庫同步完成！共計寫入 {len(full_tactics)} 個 S/A 級戰法。")

    except Exception as e:
        print(f"⚠️ 線上鏡像抓取戰法失敗: {e}")

if __name__ == "__main__":
    fetch_and_build_complete_database()
