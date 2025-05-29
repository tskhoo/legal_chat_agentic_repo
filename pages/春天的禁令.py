import streamlit as st
from datetime import date

st.set_page_config(page_title="跳板禁制令生成器", layout="centered")

st.title("⚖️ 跳板禁制令草稿生成器（香港）")

st.markdown("请填写以下信息。完成后，点击 **生成** 按钮以创建您的禁制令草稿。")

# --- 输入字段 ---
st.header("🔍 案件信息")
case_number = st.text_input("高等法院案件编号（例如：HCA 1234/2025）", value="HCA 452/2025")
claimant = st.text_input("原告姓名", value="ABC Technology Limited")
defendant = st.text_input("被告姓名", value="John Lee")

# --- 关键事实 ---
st.header("📄 关键事实")
relationship = st.text_area("描述原告与被告之间的关系（例如：雇主与雇员、业务合作伙伴等）",
                             value="被告是在2020年至2024年期間由原告僱用的高級軟件工程師。", height=100)
confidential_info = st.text_area("被指滥用的机密信息包括哪些？", 
                                 value="申索人的專有金融科技平台的源代碼、客戶名單、定價策略和內部技術架構。", height=100)
misuse_details = st.text_area("被告是如何滥用这些信息的？",
                              value="被告辭職後，加入了一間競爭對手公司，並複製了原告平台的功能，使用了在任職期間所開發的架構和代碼。",
                                height=100)
competitive_advantage = st.text_area("请说明因此获得的不公平竞争优势",
                                     value="被告的新僱主能夠提前六個月推出一款競爭產品，繞過了原告多年的研發投資。",
                                       height=100)
ongoing_risk = st.text_area("为什么这对原告仍构成持续的威胁或损害？",
                            value="原告持續失去客戶給被告的公司，而專有信息仍在被告手中使用。",
                              height=100)
duration = st.text_input("建议的禁制令持续时间（例如：6个月）", value="六個月")

# --- 提交按钮 ---
if st.button("🚀 生成跳板禁制令"):

    st.subheader("📑 生成的草稿")

    injunction = f"""
    香港特别行政区 高等法院 原讼法庭
    案件编号：{case_number}

    原告：
    {claimant}

    被告：
    {defendant}

    ------------------------------

    原讼传票 / 临时禁制令申请

    请有关各方于法院指定的日期出庭，向法官说明为何不应依据下列条款颁布禁制令：

    要求的救济

    1. 禁制令内容如下，禁止被告：
       - 使用或披露其与原告关系期间获得的机密信息；
       - 招揽原告的客户或雇员；
       - 利用所获得的不公平竞争优势从事竞争业务。

    2. 该禁制令自本命令颁布日起生效，持续 {duration}。

    3. 命令被告归还或删除其所持有的所有机密资料。

    4. 要求被告赔偿因滥用机密信息而获得的利润，或作出利润交代。

    5. 本次申请的诉讼费用。

    申请理由

    - 被告为前{relationship}，期间接触到机密信息，包括：{confidential_info}
    - 被告通过以下方式滥用了该等信息：{misuse_details}
    - 此行为使被告获得了不公平竞争优势：{competitive_advantage}
    - 此优势对原告商业利益构成持续威胁：{ongoing_risk}
    - 为防止进一步损害，禁制令为必要措施，仅赔偿金不足以补偿损失。

    日期：{date.today().strftime("%Y-%m-%d")}
    """

    st.code(injunction, language='markdown')

    st.download_button("📥 下载草稿文本", data=injunction, file_name="跳板禁制令草稿.txt")
