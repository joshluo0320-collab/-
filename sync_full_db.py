import json
import os

def generate_full_database():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    # -------------------------------------------------------------
    # 1. 全五星武將資料庫 (依陣營分類收錄)
    # -------------------------------------------------------------
    raw_generals = [
        # --- 魏國 (WEI) ---
        {"id": "cao_cao", "name": "曹操", "camp": "WEI", "cost": 7, "apt": ["S","S","A","A"], "base": [72.0, 91.0, 99.0, 64.0], "growth": [1.33, 1.94, 2.70, 1.18], "t_id": "亂世奸雄", "t_type": "Command"},
        {"id": "sima_yi", "name": "司馬懿", "camp": "WEI", "cost": 7, "apt": ["A","S","A","S"], "base": [64.0, 98.0, 98.0, 41.0], "growth": [0.81, 2.67, 2.06, 0.65], "t_id": "鷹視狼顧", "t_type": "Command"},
        {"id": "man_chong", "name": "滿寵", "camp": "WEI", "cost": 6, "apt": ["B","S","B","A"], "base": [64.0, 84.0, 85.0, 55.0], "growth": [0.75, 2.08, 1.95, 0.92], "t_id": "鎮楫左右", "t_type": "Command"},
        {"id": "sp_xunyu", "name": "SP荀彧", "camp": "WEI", "cost": 7, "apt": ["S","B","A","C"], "base": [31.0, 95.0, 87.0, 52.0], "growth": [0.28, 2.63, 1.86, 0.74], "t_id": "機鑑先識", "t_type": "Command"},
        {"id": "sp_guojia", "name": "SP郭嘉", "camp": "WEI", "cost": 7, "apt": ["S","C","S","B"], "base": [23.0, 96.0, 78.0, 67.0], "growth": [0.20, 2.64, 1.66, 1.05], "t_id": "經天緯地", "t_type": "Command"},
        {"id": "sp_pangde", "name": "SP龐德", "camp": "WEI", "cost": 6, "apt": ["S","A","S","A"], "base": [89.0, 72.0, 89.0, 61.0], "growth": [2.31, 0.85, 1.72, 1.12], "t_id": "死戰拔罪", "t_type": "Passive"},
        {"id": "jia_xu", "name": "賈詡", "camp": "WEI", "cost": 7, "apt": ["S","A","S","B"], "base": [41.0, 97.0, 88.0, 58.0], "growth": [0.35, 2.65, 1.77, 0.81], "t_id": "營謀神算", "t_type": "Active"},
        {"id": "guo_jia", "name": "郭嘉", "camp": "WEI", "cost": 5, "apt": ["S","C","A","C"], "base": [15.0, 96.0, 72.0, 67.0], "growth": [0.12, 2.64, 1.56, 1.13], "t_id": "十勝十敗", "t_type": "Passive"},
        {"id": "zhang_liao", "name": "張遼", "camp": "WEI", "cost": 7, "apt": ["S","B","B","S"], "base": [92.0, 78.0, 95.0, 77.0], "growth": [2.33, 1.09, 1.74, 1.43], "t_id": "陷陣突襲", "t_type": "Passive"},
        {"id": "xiahou_yuan", "name": "夏侯淵", "camp": "WEI", "cost": 5, "apt": ["S","B","S","C"], "base": [91.0, 68.0, 78.0, 75.0], "growth": [2.07, 0.84, 1.28, 1.33], "t_id": "將行其疾", "t_type": "Assault"},
        {"id": "xiahou_dun", "name": "夏侯惇", "camp": "WEI", "cost": 6, "apt": ["S","A","B","S"], "base": [90.0, 63.0, 89.0, 61.0], "growth": [2.10, 0.84, 2.07, 1.18], "t_id": "剛烈不屈", "t_type": "Passive"},
        {"id": "cao_ren", "name": "曹仁", "camp": "WEI", "cost": 6, "apt": ["A","S","B","S"], "base": [86.0, 62.0, 89.0, 48.0], "growth": [1.26, 0.77, 2.31, 0.79], "t_id": "固若金湯", "t_type": "Active"},
        {"id": "cheng_yu", "name": "程昱", "camp": "WEI", "cost": 6, "apt": ["S","C","A","C"], "base": [49.0, 92.0, 70.0, 47.0], "growth": [0.42, 2.32, 1.36, 0.77], "t_id": "十面埋伏", "t_type": "Active"},
        {"id": "xun_yu", "name": "荀彧", "camp": "WEI", "cost": 5, "apt": ["A","C","A","C"], "base": [26.0, 95.0, 82.0, 43.0], "growth": [0.22, 2.49, 1.62, 0.68], "t_id": "王佐之才", "t_type": "Command"},
        {"id": "wang_shuang", "name": "王雙", "camp": "WEI", "cost": 6, "apt": ["B","S","C","A"], "base": [88.0, 31.0, 79.0, 52.0], "growth": [2.24, 0.31, 1.54, 0.89], "t_id": "震駭流星", "t_type": "Active"},
        {"id": "deng_ai", "name": "鄧艾", "camp": "WEI", "cost": 6, "apt": ["A","B","A","S"], "base": [83.0, 86.0, 82.0, 65.0], "growth": [1.48, 1.66, 1.69, 1.25], "t_id": "暗度陳倉", "t_type": "Active"},
        {"id": "zhong_hui", "name": "鍾會", "camp": "WEI", "cost": 6, "apt": ["B","B","S","A"], "base": [69.0, 88.0, 79.0, 65.0], "growth": [1.12, 2.01, 1.52, 1.25], "t_id": "精練策數", "t_type": "Active"},
        {"id": "xu_chu", "name": "許褚", "camp": "WEI", "cost": 6, "apt": ["A","S","C","S"], "base": [96.0, 36.0, 75.0, 51.0], "growth": [2.65, 0.32, 1.48, 0.85], "t_id": "虎癡", "t_type": "Passive"},
        {"id": "dian_wei", "name": "典韋", "camp": "WEI", "cost": 6, "apt": ["A","S","C","S"], "base": [95.0, 35.0, 82.0, 59.0], "growth": [2.60, 0.30, 1.83, 0.99], "t_id": "古之惡來", "t_type": "Passive"},
        {"id": "yu_jin", "name": "于禁", "camp": "WEI", "cost": 5, "apt": ["A","S","A","S"], "base": [78.0, 74.0, 83.0, 48.0], "growth": [1.71, 0.95, 1.48, 0.77], "t_id": "持節撫軍", "t_type": "Active"},
        {"id": "yue_jin", "name": "樂進", "camp": "WEI", "cost": 5, "apt": ["S","A","B","S"], "base": [84.0, 68.0, 79.0, 66.0], "growth": [1.83, 0.75, 1.77, 1.11], "t_id": "臨戰先登", "t_type": "Active"},
        {"id": "hao_zhao", "name": "郝昭", "camp": "WEI", "cost": 6, "apt": ["A","S","S","B"], "base": [79.0, 89.0, 86.0, 41.0], "growth": [1.65, 1.95, 1.89, 0.65], "t_id": "金城湯池", "t_type": "Command"},

        # --- 蜀國 (SHU) ---
        {"id": "liu_bei", "name": "劉備", "camp": "SHU", "cost": 7, "apt": ["A","S","A","A"], "base": [77.0, 74.0, 81.0, 53.0], "growth": [1.18, 1.58, 2.04, 0.79], "t_id": "仁德載世", "t_type": "Command"},
        {"id": "guan_yu", "name": "關羽", "camp": "SHU", "cost": 7, "apt": ["S","A","A","S"], "base": [97.0, 79.0, 97.0, 74.0], "growth": [2.68, 1.05, 2.04, 1.32], "t_id": "威震華夏", "t_type": "Active"},
        {"id": "zhang_fei", "name": "張飛", "camp": "SHU", "cost": 6, "apt": ["A","S","C","S"], "base": [98.0, 30.0, 94.0, 80.0], "growth": [2.69, 0.22, 1.69, 1.26], "t_id": "燕人咆哮", "t_type": "Passive"},
        {"id": "sp_guanyu", "name": "SP關羽", "camp": "SHU", "cost": 7, "apt": ["S","A","A","S"], "base": [96.0, 77.0, 98.0, 74.0], "growth": [2.70, 1.05, 2.12, 1.33], "t_id": "水淹七軍", "t_type": "Active"},
        {"id": "zhu_ge_liang", "name": "諸葛亮", "camp": "SHU", "cost": 7, "apt": ["C","B","S","S"], "base": [38.0, 100.0, 95.0, 55.0], "growth": [0.38, 3.00, 2.36, 0.90], "t_id": "神機妙算", "t_type": "Command"},
        {"id": "sp_zhugeliang", "name": "SP諸葛亮", "camp": "SHU", "cost": 7, "apt": ["C","B","S","S"], "base": [37.0, 100.0, 98.0, 56.0], "growth": [0.38, 3.00, 2.38, 0.92], "t_id": "錦囊妙計", "t_type": "Command"},
        {"id": "pang_tong", "name": "龐統", "camp": "SHU", "cost": 7, "apt": ["C","B","S","A"], "base": [34.0, 97.0, 85.0, 51.0], "growth": [0.31, 2.61, 1.79, 0.72], "t_id": "連環計", "t_type": "Active"},
        {"id": "jiang_wei", "name": "姜維", "camp": "SHU", "cost": 7, "apt": ["S","A","S","A"], "base": [89.0, 90.0, 92.0, 64.0], "growth": [2.01, 2.03, 1.91, 1.07], "t_id": "義膽雄心", "t_type": "Passive"},
        {"id": "zhao_yun", "name": "趙雲", "camp": "SHU", "cost": 7, "apt": ["S","A","A","S"], "base": [96.0, 77.0, 96.0, 66.0], "growth": [2.62, 0.96, 2.07, 1.11], "t_id": "一身是膽", "t_type": "Passive"},
        {"id": "guan_yinping", "name": "關銀屏", "camp": "SHU", "cost": 6, "apt": ["S","B","B","S"], "base": [82.0, 52.0, 81.0, 66.0], "growth": [2.09, 0.98, 1.45, 1.21], "t_id": "將門虎女", "t_type": "Active"},
        {"id": "wei_yan", "name": "魏延", "camp": "SHU", "cost": 6, "apt": ["A","S","A","S"], "base": [92.0, 69.0, 85.0, 66.0], "growth": [2.37, 0.92, 1.48, 1.21], "t_id": "奇兵間道", "t_type": "Passive"},
        {"id": "fa_zheng", "name": "法正", "camp": "SHU", "cost": 4, "apt": ["C","A","A","A"], "base": [38.0, 94.0, 76.0, 49.0], "growth": [0.33, 2.21, 1.45, 0.71], "t_id": "以逸待勞", "t_type": "Active"},
        {"id": "huang_zhong", "name": "黃忠", "camp": "SHU", "cost": 6, "apt": ["A","S","S","B"], "base": [93.0, 65.0, 87.0, 53.0], "growth": [2.30, 0.75, 1.54, 0.81], "t_id": "百步穿楊", "t_type": "Active"},
        {"id": "ma_chao", "name": "馬超", "camp": "SHU", "cost": 7, "apt": ["S","B","B","S"], "base": [97.0, 44.0, 88.0, 78.0], "growth": [2.65, 0.35, 1.55, 1.45], "t_id": "槊血縱橫", "t_type": "Passive"},
        {"id": "huang_yueying", "name": "黃月英", "camp": "SHU", "cost": 4, "apt": ["C","C","C","C"], "base": [29.0, 88.0, 68.0, 60.0], "growth": [0.25, 2.11, 1.24, 1.01], "t_id": "工神", "t_type": "Command"},
        {"id": "xu_shu", "name": "徐庶", "camp": "SHU", "cost": 6, "apt": ["S","C","A","C"], "base": [42.0, 93.0, 78.0, 52.0], "growth": [0.35, 2.33, 1.45, 0.85], "t_id": "處茲不惑", "t_type": "Active"},
        {"id": "yan_yan", "name": "嚴顏", "camp": "SHU", "cost": 6, "apt": ["A","A","S","S"], "base": [83.0, 68.0, 85.0, 59.0], "growth": [1.91, 0.78, 1.75, 1.01], "t_id": "不屈不撓", "t_type": "Active"},

        # --- 吳國 (WU) ---
        {"id": "lu_xun", "name": "陸遜", "camp": "WU", "cost": 7, "apt": ["A","B","S","S"], "base": [69.0, 95.0, 94.0, 32.0], "growth": [0.60, 2.60, 1.88, 0.51], "t_id": "火燒連營", "t_type": "Active"},
        {"id": "tai_shi_ci", "name": "太史慈", "camp": "WU", "cost": 6, "apt": ["S","C","S","B"], "base": [93.0, 69.0, 90.0, 67.0], "growth": [2.09, 0.77, 1.49, 1.11], "t_id": "神射", "t_type": "Passive"},
        {"id": "zhou_tai", "name": "周泰", "camp": "WU", "cost": 6, "apt": ["S","S","A","A"], "base": [84.0, 48.0, 95.0, 51.0], "growth": [1.54, 0.58, 2.08, 0.81], "t_id": "肉身鐵壁", "t_type": "Passive"},
        {"id": "sun_shang_xiang", "name": "孫尚香", "camp": "WU", "cost": 6, "apt": ["S","B","S","B"], "base": [86.0, 63.0, 80.0, 71.0], "growth": [2.39, 0.85, 1.46, 1.25], "t_id": "弓腰姬", "t_type": "Passive"},
        {"id": "sun_quan", "name": "孫權", "camp": "WU", "cost": 7, "apt": ["A","B","S","A"], "base": [79.0, 80.0, 89.0, 67.0], "growth": [1.63, 1.65, 1.67, 1.14], "t_id": "坐斷東南", "t_type": "Command"},
        {"id": "cheng_pu", "name": "程普", "camp": "WU", "cost": 5, "apt": ["B","A","A","S"], "base": [79.0, 79.0, 84.0, 51.0], "growth": [1.19, 1.44, 2.06, 0.89], "t_id": "勇烈持重", "t_type": "Passive"},
        {"id": "sp_lv_meng", "name": "SP呂蒙", "camp": "WU", "cost": 7, "apt": ["A","B","S","S"], "base": [81.0, 91.0, 91.0, 55.0], "growth": [1.71, 1.89, 1.95, 0.95], "t_id": "溯江搖櫓", "t_type": "Passive"},
        {"id": "lu_su", "name": "魯肅", "camp": "WU", "cost": 6, "apt": ["B","A","S","B"], "base": [43.0, 92.0, 84.0, 53.0], "growth": [0.38, 2.47, 1.66, 0.81], "t_id": "濟貧好施", "t_type": "Command"},
        {"id": "zhou_yu", "name": "周瑜", "camp": "WU", "cost": 7, "apt": ["B","B","S","A"], "base": [71.0, 96.0, 95.0, 42.0], "growth": [0.82, 2.69, 1.66, 0.61], "t_id": "神火計", "t_type": "Passive"},
        {"id": "sp_zhouyu", "name": "SP周瑜", "camp": "WU", "cost": 7, "apt": ["B","B","S","A"], "base": [72.0, 96.0, 96.0, 43.0], "growth": [0.82, 2.69, 1.70, 0.62], "t_id": "江天夜雨", "t_type": "Command"},
        {"id": "gan_ning", "name": "甘寧", "camp": "WU", "cost": 6, "apt": ["A","A","S","S"], "base": [94.0, 76.0, 86.0, 70.0], "growth": [2.60, 0.90, 1.59, 1.25], "t_id": "錦帆百狩", "t_type": "Passive"},
        {"id": "lv_meng", "name": "呂蒙", "camp": "WU", "cost": 6, "apt": ["B","B","S","S"], "base": [81.0, 89.0, 91.0, 52.0], "growth": [1.68, 1.81, 1.89, 0.90], "t_id": "白衣渡江", "t_type": "Command"},
        {"id": "ling_tong", "name": "凌統", "camp": "WU", "cost": 6, "apt": ["S","A","B","A"], "base": [89.0, 60.0, 80.0, 77.0], "growth": [1.97, 0.68, 1.51, 1.48], "t_id": "國士將風", "t_type": "Command"},
        {"id": "sun_ce", "name": "孫策", "camp": "WU", "cost": 5, "apt": ["S","A","A","S"], "base": [92.0, 74.0, 88.0, 68.0], "growth": [2.07, 0.93, 1.45, 1.18], "t_id": "江東小霸王", "t_type": "Passive"},
        {"id": "sun_jian", "name": "孫堅", "camp": "WU", "cost": 6, "apt": ["A","S","A","S"], "base": [90.0, 79.0, 94.0, 40.0], "growth": [2.00, 1.05, 2.05, 0.65], "t_id": "江東猛虎", "t_type": "Active"},

        # --- 群雄 (QUN) ---
        {"id": "zhang_jiao", "name": "張角", "camp": "QUN", "cost": 7, "apt": ["B","S","S","B"], "base": [27.0, 93.0, 84.0, 38.0], "growth": [0.32, 2.38, 1.77, 0.58], "t_id": "五雷轟頂", "t_type": "Active"},
        {"id": "lv_bu", "name": "呂布", "camp": "QUN", "cost": 7, "apt": ["S","B","S","A"], "base": [100.0, 26.0, 97.0, 74.0], "growth": [3.00, 0.27, 1.40, 1.41], "t_id": "天下無雙", "t_type": "Active"},
        {"id": "sp_machao", "name": "SP馬超", "camp": "QUN", "cost": 7, "apt": ["S","B","B","S"], "base": [98.0, 45.0, 89.0, 81.0], "growth": [2.75, 0.35, 1.60, 1.51], "t_id": "看破萬陣", "t_type": "Passive"},
        {"id": "sp_huangyueying", "name": "SP黃月英", "camp": "QUN", "cost": 5, "apt": ["B","B","S","B"], "base": [32.0, 90.0, 72.0, 62.0], "growth": [0.28, 2.25, 1.35, 1.05], "t_id": "靈機巧動", "t_type": "Command"},
        {"id": "sp_yuan_shao", "name": "SP袁紹", "camp": "QUN", "cost": 7, "apt": ["A","A","S","A"], "base": [82.0, 75.0, 81.0, 62.0], "growth": [2.06, 1.48, 1.79, 1.04], "t_id": "高櫓連營", "t_type": "Passive"},
        {"id": "sp_zhujun", "name": "SP朱儁", "camp": "QUN", "cost": 6, "apt": ["A","B","S","A"], "base": [65.0, 89.0, 89.0, 48.0], "growth": [1.10, 1.88, 1.75, 0.77], "t_id": "圍師必闕", "t_type": "Command"},
        {"id": "zuo_ci", "name": "左慈", "camp": "QUN", "cost": 5, "apt": ["C","C","C","C"], "base": [21.0, 94.0, 70.0, 35.0], "growth": [0.18, 2.45, 1.45, 0.55], "t_id": "金丹秘術", "t_type": "Command"},
        {"id": "yu_ji", "name": "于吉", "camp": "QUN", "cost": 5, "apt": ["C","B","B","C"], "base": [18.0, 92.0, 68.0, 40.0], "growth": [0.15, 2.40, 1.50, 0.60], "t_id": "興雲布雨", "t_type": "Command"},
        {"id": "diao_chan", "name": "貂蟬", "camp": "QUN", "cost": 5, "apt": ["C","B","B","C"], "base": [26.0, 81.0, 71.0, 72.0], "growth": [0.24, 1.95, 1.35, 1.25], "t_id": "閉月", "t_type": "Active"},
        {"id": "hua_tuo", "name": "華佗", "camp": "QUN", "cost": 5, "apt": ["C","C","A","C"], "base": [25.0, 91.0, 78.0, 51.0], "growth": [0.25, 2.10, 1.55, 0.81], "t_id": "青囊", "t_type": "Command"},
        {"id": "yuan_shao", "name": "袁紹", "camp": "QUN", "cost": 6, "apt": ["A","A","S","A"], "base": [80.0, 70.0, 81.0, 62.0], "growth": [1.83, 1.25, 1.71, 1.04], "t_id": "累世立名", "t_type": "Active"},
        {"id": "dong_zhuo", "name": "董卓", "camp": "QUN", "cost": 7, "apt": ["S","A","B","A"], "base": [87.0, 73.0, 90.0, 52.0], "growth": [1.85, 1.35, 2.07, 0.81], "t_id": "酒池肉林", "t_type": "Passive"},
        {"id": "tian_feng", "name": "田豐", "camp": "QUN", "cost": 5, "apt": ["C","S","A","C"], "base": [31.0, 93.0, 79.0, 45.0], "growth": [0.31, 2.42, 1.48, 0.69], "t_id": "竭忠盡智", "t_type": "Active"},
        {"id": "wen_chou", "name": "文醜", "camp": "QUN", "cost": 5, "apt": ["A","A","S","S"], "base": [93.0, 25.0, 84.0, 68.0], "growth": [2.18, 0.22, 1.51, 1.12], "t_id": "登鋒陷陣", "t_type": "Active"},
        {"id": "yan_liang", "name": "顏良", "camp": "QUN", "cost": 5, "apt": ["S","A","A","S"], "base": [94.0, 38.0, 80.0, 65.0], "growth": [2.22, 0.40, 1.38, 1.05], "t_id": "勇冠三軍", "t_type": "Assault"}
    ]

    generals_db = []
    for g in raw_generals:
        generals_db.append({
            "id": g["id"],
            "name": g["name"],
            "camp": g["camp"],
            "cost": g["cost"],
            "base_aptitude": {
                "Cavalry": g["apt"][0],
                "Shield": g["apt"][1],
                "Bow": g["apt"][2],
                "Spear": g["apt"][3]
            },
            "base_stats": {
                "force": g["base"][0],
                "intelligence": g["base"][1],
                "command": g["base"][2],
                "speed": g["base"][3]
            },
            "stat_growth": {
                "force": g["growth"][0],
                "intelligence": g["growth"][1],
                "command": g["growth"][2],
                "speed": g["growth"][3]
            },
            "innate_tactic_id": g["t_id"],
            "innate_tactic_type": g["t_type"],
            "tags": {"role": ["Core"], "stat_scaling": ["intelligence" if g["base"][1] > g["base"][0] else "force"]}
        })

    # -------------------------------------------------------------
    # 2. 全主流 S 級戰法庫 (事件 + 傳承 + 陣法 + 兵種)
    # -------------------------------------------------------------
    raw_tactics = [
        # --- 防禦/續航/減傷/淨化核心 ---
        {"id": "cao_chuan_jie_jian", "name": "草船借箭", "type": "Active", "rate": 0.65, "prio": 5, "tags": ["S_Tier_Defense", "Purify", "Recovery"]},
        {"id": "fu_ji_jun_min", "name": "撫輯軍民", "type": "Command", "rate": 1.0, "prio": 4, "tags": ["S_Tier_Defense", "Pre_Round_Reduction"]},
        {"id": "zan_bi_qi_feng", "name": "暫避其鋒", "type": "Command", "rate": 1.0, "prio": 4, "tags": ["S_Tier_Defense", "Burst_Protection"]},
        {"id": "gua_gu_liao_du", "name": "刮骨療毒", "type": "Active", "rate": 0.40, "prio": 5, "tags": ["Targeted_Purify", "Emergency_Recovery"]},
        {"id": "ying_cheng_zi_shou", "name": "嬰城自守", "type": "Active", "rate": 0.50, "prio": 5, "tags": ["Recovery"]},
        {"id": "bei_she_gui_che", "name": "杯蛇鬼車", "type": "Active", "rate": 0.50, "prio": 5, "tags": ["Damage", "Recovery"]},
        {"id": "fei_gong_zhi_sheng", "name": "非攻制勝", "type": "Command", "rate": 1.0, "prio": 4, "tags": ["Recovery", "Weapon_Synergy"]},
        {"id": "yu_di_ping_zhang", "name": "御敵屏障", "type": "Command", "rate": 1.0, "prio": 4, "tags": ["Defense_Reduction"]},
        {"id": "zuo_shou_meng_jin", "name": "坐守孤城", "type": "Active", "rate": 0.45, "prio": 5, "tags": ["Recovery"]},
        {"id": "zheng_zhuang_dai_fa", "name": "整裝待發", "type": "Command", "rate": 1.0, "prio": 4, "tags": ["Recovery"]},

        # --- 控制與反制核心 ---
        {"id": "dang_feng_cui_jue", "name": "當鋒摧決", "type": "Assault", "rate": 0.35, "prio": 6, "tags": ["Core_Breaker", "Pseudo_Report"]},
        {"id": "sheng_qi_ling_di", "name": "盛氣凌敵", "type": "Command", "rate": 1.0, "prio": 4, "tags": ["Disarm", "Pre_Round_Control"]},
        {"id": "ba_men_jin_suo", "name": "八門金鎖陣", "type": "Formation", "rate": 1.0, "prio": 2, "tags": ["Pre_Round_Reduction", "First_Strike"]},
        {"id": "wei_tian_gong_li", "name": "威謀靡亢", "type": "Active", "rate": 0.40, "prio": 5, "tags": ["Weakness", "True_Damage"]},
        {"id": "wo_xin_chang_dan", "name": "臥薪嘗膽", "type": "Active", "rate": 0.45, "prio": 5, "tags": ["Stun", "Burst"]},
        {"id": "mei_huo", "name": "魅惑", "type": "Passive", "rate": 1.0, "prio": 1, "tags": ["Counter_Control", "Tank_Synergy"]},

        # --- 陣法 (Formation) ---
        {"id": "feng_shi_zhen", "name": "鋒矢陣", "type": "Formation", "rate": 1.0, "prio": 2, "tags": ["Single_Core_Amplifier"]},
        {"id": "san_shi_zhen", "name": "三勢陣", "type": "Formation", "rate": 1.0, "prio": 2, "tags": ["Mixed_Camp_Amplifier"]},
        {"id": "ji_xing_zhen", "name": "箕形陣", "type": "Formation", "rate": 1.0, "prio": 2, "tags": ["Anti_Main_Burst"]},
        {"id": "xing_ji_zhen", "name": "形機能陣", "type": "Formation", "rate": 1.0, "prio": 2, "tags": ["Formation"]},
        {"id": "wu_feng_zhen", "name": "武鋒陣", "type": "Formation", "rate": 1.0, "prio": 2, "tags": ["Attract_Fire", "Ramp_Up"]},
        {"id": "qian_long_zhen", "name": "潛龍陣", "type": "Formation", "rate": 1.0, "prio": 2, "tags": ["Sub_General_Main_Skill"]},

        # --- 兵種 (Troop Special) ---
        {"id": "teng_jia_bing", "name": "藤甲兵", "type": "Troop", "rate": 1.0, "prio": 3, "tags": ["Extreme_Physical_Defense", "Fire_Weakness"]},
        {"id": "xian_zhen_ying", "name": "陷陣營", "type": "Troop", "rate": 1.0, "prio": 3, "tags": ["Shield_Buff", "First_Heal"]},
        {"id": "hu_chen_jun", "name": "虎豹騎", "type": "Troop", "rate": 1.0, "prio": 3, "tags": ["Assault_Rate_Buff"]},
        {"id": "xi_liang_tie_qi", "name": "西涼鐵騎", "type": "Troop", "rate": 1.0, "prio": 3, "tags": ["Crit_Rate_Buff"]},
        {"id": "bai_ma_yi_cong", "name": "白馬義從", "type": "Troop", "rate": 1.0, "prio": 3, "tags": ["First_Strike", "Active_Rate_Buff"]},
        {"id": "wu_dang_fei_jun", "name": "無當飛軍", "type": "Troop", "rate": 1.0, "prio": 3, "tags": ["Stat_Buff", "Poison_Damage"]},
        {"id": "qing_zhou_bing", "name": "青州兵", "type": "Troop", "rate": 1.0, "prio": 3, "tags": ["Counter_Attack", "Heal_Turn3"]},
        {"id": "da_ji_shi", "name": "大戟士", "type": "Troop", "rate": 1.0, "prio": 3, "tags": ["Normal_Attack_AOE"]},
        {"id": "jin_fan_jun", "name": "錦帆軍", "type": "Troop", "rate": 1.0, "prio": 3, "tags": ["Bleed_Damage", "Heal"]},
        {"id": "fei_xiong_jun", "name": "飛熊軍", "type": "Troop", "rate": 1.0, "prio": 3, "tags": ["Heal_Converted_Damage"]},

        # --- 謀略核心輸出 ---
        {"id": "shi_bie_san_ri", "name": "士別三日", "type": "Passive", "rate": 1.0, "prio": 1, "tags": ["Mage_Survival", "Turn4_Burst"]},
        {"id": "yong_wu_tong_shen", "name": "用武通神", "type": "Passive", "rate": 1.0, "prio": 1, "tags": ["Late_Turn_Stable_Damage"]},
        {"id": "tai_ping_dao_fa", "name": "太平道法", "type": "Passive", "rate": 1.0, "prio": 1, "tags": ["Mage_Crit", "Rate_Boost"]},
        {"id": "duo_hun_xie_po", "name": "奪魂挾魄", "type": "Active", "rate": 0.55, "prio": 5, "tags": ["Stat_Steal", "Debuff"]},
        {"id": "chen_sha_jue_ji", "name": "沈沙決水", "type": "Active", "rate": 0.40, "prio": 5, "tags": ["Water_Damage", "Damage_Amplifier"]},
        {"id": "si_bie_san_ri", "name": "四面楚歌", "type": "Active", "rate": 0.50, "prio": 5, "tags": ["Poison_Damage"]},
        {"id": "yan_zhi_you_dao", "name": "焰逐風飛", "type": "Active", "rate": 0.35, "prio": 5, "tags": ["Stun", "Mage_Damage"]},
        {"id": "zhong_zhi_cheng_cheng", "name": "眾志成城", "type": "Passive", "rate": 1.0, "prio": 1, "tags": ["Heal", "Tactical_Damage"]},

        # --- 兵刃核心輸出與突擊 ---
        {"id": "heng_sao_qian_jun", "name": "橫掃千軍", "type": "Active", "rate": 0.40, "prio": 5, "tags": ["AOE_Damage", "Stun_Synergy"]},
        {"id": "po_zhen_cui_jian", "name": "破陣摧堅", "type": "Active", "rate": 0.35, "prio": 5, "tags": ["Armor_Pierce", "Weapon_Damage"]},
        {"id": "suo_xiang_pi_mi", "name": "所向披靡", "type": "Active", "rate": 0.30, "prio": 5, "tags": ["High_AOE_Physical"]},
        {"id": "luo_yi_xue_zhan", "name": "裸衣血戰", "type": "Passive", "rate": 1.0, "prio": 1, "tags": ["Continuous_Attack", "Armor_Shed"]},
        {"id": "yi_ji_dang_qian", "name": "一騎當千", "type": "Assault", "rate": 0.30, "prio": 6, "tags": ["Assault_AOE"]},
        {"id": "bai_qi_jie_ying", "name": "百騎劫營", "type": "Assault", "rate": 0.40, "prio": 6, "tags": ["Assault_Main_Snipe"]},
        {"id": "gui_shen_ting_wei", "name": "鬼神霆威", "type": "Assault", "rate": 0.35, "prio": 6, "tags": ["Assault_Execute"]},
        {"id": "bao_li_wu_ren", "name": "暴戾無仁", "type": "Assault", "rate": 0.35, "prio": 6, "tags": ["Assault_Confusion"]},
        {"id": "zhe_chong_yu_wu", "name": "折衝禦侮", "type": "Assault", "rate": 0.45, "prio": 6, "tags": ["Protect_Main", "Armor_Pierce"]},
        {"id": "su_jie_ti_ji", "name": "速乘其利", "type": "Assault", "rate": 0.35, "prio": 6, "tags": ["Silence", "Assault"]},
        {"id": "ju_shui_duan_qiao", "name": "據水斷橋", "type": "Active", "rate": 0.40, "prio": 5, "tags": ["Debuff_Damage", "Drain"]},
        {"id": "ji_feng_zhou_yu", "name": "疾風驟雨", "type": "Active", "rate": 0.40, "prio": 5, "tags": ["Multi_Physical_Hit", "Heal_Block"]}
    ]

    tactics_db = []
    for t in raw_tactics:
        tactics_db.append({
            "id": t["id"],
            "name": t["name"],
            "grade": "S",
            "type": t["type"],
            "activation_rate": t["rate"],
            "execution_priority": t["prio"],
            "tags": {"category": t["tags"]}
        })

    # 寫入檔案
    with open(os.path.join(data_dir, "generals.json"), "w", encoding="utf-8") as f:
        json.dump(generals_db, f, ensure_ascii=False, indent=2)

    with open(os.path.join(data_dir, "tactics.json"), "w", encoding="utf-8") as f:
        json.dump(tactics_db, f, ensure_ascii=False, indent=2)

    print(f"✅ 成功同步！已收錄 {len(generals_db)} 位主流全五星武將，以及 {len(tactics_db)} 個全主流 S 級戰法。")

if __name__ == "__main__":
    generate_full_database()
