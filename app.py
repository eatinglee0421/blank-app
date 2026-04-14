import streamlit as st

# 設定網頁標題與風格
st.set_page_config(page_title="MIBC Decision Support", layout="wide")

# 自定義 CSS 讓介面更專業
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stAlert {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_stdio=True)

st.title("🛡️ MIBC 臨床治療決策支援系統 (含 NIAGARA 方案)")
st.info("本系統整合了最新 NIAGARA 臨床試驗數據，協助評估周術期 Durvalumab 的適用性。")
st.markdown("---")

# --- 側邊欄：病人參數 ---
with st.sidebar:
    st.header("📋 病人基本參數")
    gender = st.selectbox("性別", ["Male", "Female"])
    age = st.number_input("年齡", min_value=18, max_value=100, value=65)
    weight = st.number_input("體重 (kg)", min_value=30, max_value=200, value=70)
    creat = st.number_input("血清肌酸酐 (sCr, mg/dL)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
    
    st.markdown("---")
    ecog = st.slider("ECOG 體能評分", 0, 4, 0)
    autoimmune = st.checkbox("患有活動性自體免疫疾病")

# --- 計算腎功能 (Cockcroft-Gault) ---
def calculate_crcl(gender, age, weight, creat):
    factor = 0.85 if gender == "Female" else 1.0
    return ((140 - age) * weight) / (72 * creat) * factor

crcl = calculate_crcl(gender, age, weight, creat)

# --- 主畫面佈局 ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔍 臨床狀況評估")
    ct_stage = st.selectbox("臨床分期 (cT Stage)", [
        "cT2-cT4a, N0M0 (肌層浸潤)", 
        "cT4b (局部晚期)", 
        "N+ (淋巴結轉移)", 
        "M1 (遠端轉移)"
    ])
    fit_for_surgery = st.toggle("病人體能可承受根除性手術 (RC)", value=True)
    bladder_preservation = st.toggle("病人強烈希望保留膀胱 (TMT)", value=False)

with col2:
    st.subheader("📈 生理指標結果")
    st.metric("估算 CrCl", f"{crcl:.1f} ml/min")
    
    # 判定 Cisplatin 適合度
    cis_eligible = crcl >= 60 and ecog <= 1
    if cis_eligible:
        st.success("✅ 符合 Cisplatin 使用標準 (Cis-Eligible)")
    else:
        st.warning("⚠️ Cisplatin-Ineligible (腎功能或體能限制)")

st.markdown("---")

# --- 決策邏輯引擎 ---
st.subheader("💡 臨床決策建議 (Decision Logic)")

if "cT2-cT4a" in ct_stage:
    # 1. NIAGARA 方案路徑 (最優先)
    if cis_eligible and fit_for_surgery and not bladder_preservation:
        st.success("### 🚀 首選建議：NIAGARA 方案 (Perioperative Durvalumab)")
        st.markdown("""
        **根據 NIAGARA 試驗結果，此病人符合周術期免疫化療標準：**
        * **術前 (Neoadjuvant):** Durvalumab (1500mg) + Gem/Cis (每3週一次，共4週期)。
        * **手術 (Surgery):** 進行根除性膀胱切除術 (RC) + 盆腔淋巴結清掃。
        * **術後 (Adjuvant):** 持續使用 Durvalumab 輔助治療 (維持8個週期)。
        
        **臨床效益：** 相比單用化療，可顯著延長 EFS (無事件生存期) 與 OS (總生存期)。
        """)
        if autoimmune:
            st.error("⚠️ 警告：病人有自體免疫病史，使用 Durvalumab 前需由免疫專科會診評估風險。")

    # 2. 膀胱保留路徑 (TMT)
    elif bladder_preservation:
        st.info("### 建議方案：三合一保留療法 (Trimodality Therapy)")
        st.markdown("""
        * **步驟：** 極大化 TURBT 切除 + 同步化放療 (CCRT)。
        * **適用指標：** 腫瘤單一、無廣泛原位癌 (CIS)、無腎水腫。
        * **備註：** 若 CCRT 後反應不佳，仍需考慮補救性膀胱切除。
        """)

    # 3. 不適合含鉑化療路徑 (Cis-Ineligible)
    elif not cis_eligible and fit_for_surgery:
        st.warning("### 建議方案：直接手術 + 術後輔助免疫治療")
        st.markdown("""
        * **術前：** 由於不適合 Cisplatin，建議直接進行根除性手術 (RC)。
        * **術後 (CheckMate-274):** 若病理分期仍高 ($pT3+$ 或 $pN+$)，建議使用 **Nivolumab** 輔助治療。
        """)

else:
    st.error("此臨床分期非標準 MIBC 指引範圍，請轉向全身性全身化療、免疫治療或參與臨床試驗。")

# --- 腳註 ---
st.markdown("---")
st.caption("免責聲明：此程式僅供醫療專業人員學術討論與開發測試參考，實際診療請依據專業醫師判斷與最新國際治療指引。")
