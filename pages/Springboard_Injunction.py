import streamlit as st
from datetime import date

st.set_page_config(page_title="Springboard Injunction Generator", layout="centered")

st.title("⚖️ Springboard Injunction Draft Generator (HK)")

st.markdown("Fill out the details below. Once completed, click **Generate** to create your draft injunction.")

# --- Input fields ---
st.header("🔍 Case Information")
case_number = st.text_input("High Court Case Number (e.g., HCA 1234/2025)", value="HCA 452/2025")
claimant = st.text_input("Claimant's Full Name", value ="ABC Technology Limited")
defendant = st.text_input("Defendant's Full Name", value = "John Lee")

# --- Facts ---
st.header("📄 Key Facts")
relationship = st.text_area("Describe the relationship between claimant and defendant (e.g., employer-employee, \
                            business partner)", height=100, value ="The Defendant was a Senior Software Engineer \
employed by the Claimant between 2020 and 2024.")
confidential_info = st.text_area("What confidential information was allegedly misused?", 
                                 height=100, value="Source code, client lists, pricing strategies, and internal technical \
architecture of the Claimant’s proprietary fintech platform.")
misuse_details = st.text_area("How did the defendant misuse the information?", 
                              height=100, value="Source code, client lists, pricing strategies, and internal \
technical architecture of the Claimant’s proprietary fintech platform.")
competitive_advantage = st.text_area("Explain the unfair competitive advantage gained", 
                                     height=100, value="After resigning, the Defendant joined a competitor \
and replicated features of the Claimant’s platform, using the architecture \
and code developed during employment.")
ongoing_risk = st.text_area("Why is there an ongoing threat or harm to the claimant?", 
                            height=100, value="The Claimant is continuing to lose customers to the Defendant’s \
company, and the proprietary information remains in use by the Defendant.")
duration = st.text_input("Proposed duration of injunction (e.g., 6 months)", value = "6 months")

# --- Submission ---
if st.button("🚀 Generate Springboard Injunction"):

    st.subheader("📑 Generated Draft")

    injunction = f"""
    IN THE HIGH COURT OF THE HONG KONG SPECIAL ADMINISTRATIVE REGION
    COURT OF FIRST INSTANCE
    ACTION NO. {case_number}

    BETWEEN
    {claimant}
    Plaintiff

    AND
    {defendant}
    Defendant

    ------------------------------

    ORIGINATING SUMMONS / INTERLOCUTORY SUMMONS

    Let all parties concerned attend before the Honourable Judge at the High Court on a date to be fixed, to show cause why an injunction should not be granted in the following terms:

    RELIEF SOUGHT

    1. An injunction restraining the Defendant from:
       - Using or disclosing confidential information acquired during their relationship with the Plaintiff;
       - Soliciting the Plaintiff’s clients or employees;
       - Engaging in competitive business using any unfair advantage derived from such information.

    2. That the injunction remain in effect for {duration} from the date of this order.

    3. An order requiring the Defendant to return or delete all confidential materials in their possession.

    4. Damages or an account of profits obtained through misuse of confidential information.

    5. Costs of this application.

    GROUNDS FOR APPLICATION

    - The Defendant, a former {relationship}, had access to confidential information, namely: {confidential_info}
    - The Defendant misused this information by: {misuse_details}
    - This has resulted in an unfair competitive advantage: {competitive_advantage}
    - The advantage poses an ongoing risk to the Plaintiff’s commercial interests: {ongoing_risk}
    - The injunction is necessary to prevent further harm, and damages would not suffice.

    Dated: {date.today().strftime("%d %B %Y")}
    """

    st.code(injunction, language='markdown')

    st.download_button("📥 Download Draft as markdown", data=injunction, file_name="springboard_injunction_draft.md")

