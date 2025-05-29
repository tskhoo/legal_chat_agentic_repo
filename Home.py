import streamlit as st
# from openai import OpenAI
from openai import AzureOpenAI
import os
import shutil
import fitz 
import base64
  
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
# from langchain_community.vectorstores import Chroma
from langchain_community.vectorstores import FAISS

from fpdf import FPDF
import unicodedata

AZURE_ENDPOINT = "https://khoot-ma1d16zs-eastus2.cognitiveservices.azure.com/"
AZURE_MODEL = "gpt-4o"
AZURE_API_KEY = "8UNdcHUQNEE5uC768eY16kfQVclMMQMuGEM3aECivQvNbDJIKIcaJQQJ99BDACHYHv6XJ3w3AAAAACOGIenh"
AZURE_DEPLOYMENT_ID = "2024-12-01-preview"

COMPARATIVE_LEGAL_ANALYSIS_PROMPT = """ You are provided with two legal documents. Please perform a comprehensive 
                            analysis that includes the following: 
                            Compare the two documents in terms of their content, legal arguments, and conclusions. 
                            Highlight any notable similarities or differences in the reasoning, structural organization, 
                            and the case authorities cited, with each observation supported by a footnote pointing 
                            to its location in the original text in this exact format [Paragraph X, Filename : XXX]. 
                            Explain the rationale behind the decisions in each case, including the legal foundations, 
                            principles, or precedents relied upon—each accompanied by a corresponding footnote. 
                            Summarize five key facts central to the case(s)—such as the parties involved, significant 
                            events, legal issues raised, and any material facts that influenced the judgment—again, 
                            with footnotes referencing their source in the document. 
                            Analyze the judicial reasoning used to reach the final decision(s), and provide footnoted 
                            references showing how the judge(s) interpreted and applied the law to the facts. 
                            Outline the logical progression of the analysis, ensuring each step is supported by a 
                            clearly numbered footnote. 
                            When identifying and explaining case authorities cited or precedents, include footnotes that provide 
                            both the full case name and its citation number or reference [e.g., Smith v Jones [1990] HKCA 45, Filename XXX].
                            Clearly indicate where each authority appears in the document, and how it was used to support or 
                            justify the legal reasoning."""


# CASE_SUMMARIZATION_PROMPT = """  Please summarize this document in terms of their content, legal arguments, and conclusions. 
#                         Highlight any notable similarities or differences in the reasoning, 
#                         structural organization, and the case authorities cited. 
#                         Explain the rationale behind the decisions in each case. What legal 
#                         foundations, principles, or precedents were relied upon to reach the outcomes? 
#                         Summarize five key facts that are central to the case(s), such as the parties 
#                         involved, significant events, legal issues raised, and any material facts that 
#                         influenced the judgment. Analyze the judicial reasoning used to reach the 
#                         final decision(s). Describe how the judge(s) interpreted and applied the 
#                         law to the facts, and outline the logical progression of their analysis. 
#                         Identify and explain the case authorities cited in the documents. 
#                         Detail how these authorities were used to support or justify the legal reasoning."""

CASE_SUMMARIZATION_PROMPT = """Please summarize this document in terms of its content, legal arguments, and 
                            conclusions, and provide footnote references for every extracted point in this exact format [Paragraph X]. 
                            Highlight any notable similarities or differences in the reasoning, structural organization, 
                            and the case authorities cited, with each observation supported by a footnote pointing 
                            to its location in the original text in this exact format [Paragraph X]. 
                            Explain the rationale behind the decisions in each case, including the legal foundations, 
                            principles, or precedents relied upon—each accompanied by a corresponding footnote. 
                            Summarize five key facts central to the case(s)—such as the parties involved, significant 
                            events, legal issues raised, and any material facts that influenced the judgment—again, 
                            with footnotes referencing their source in the document. 
                            Analyze the judicial reasoning used to reach the final decision(s), and provide footnoted 
                            references showing how the judge(s) interpreted and applied the law to the facts. 
                            Outline the logical progression of the analysis, ensuring each step is supported by a 
                            clearly numbered footnote. 
                            When identifying and explaining case authorities cited or precedents, include footnotes that provide 
                            both the full case name and its citation number or reference [e.g., Smith v Jones [1990] HKCA 45].
                            Clearly indicate where each authority appears in the document, and how it was used to support or 
                            justify the legal reasoning."""

# --- App Config ---
st.set_page_config(page_title="Legal Q&A Chatbot", page_icon="⚖️", layout="centered")

# --- App Title ---
st.markdown(
    "<h1 style='text-align: center; color: #2c3e50;'>⚖️ Legal Assistant Chatbot</h1>",
    unsafe_allow_html=True,
)
st.markdown("<p style='text-align: center;'>Ask me any legal question and I'll explain it in simple terms.</p>", unsafe_allow_html=True)

# Initialize history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Initialize session state
if "user_question1" not in st.session_state:
    st.session_state.user_question1 = ""
if "placeholder" not in st.session_state:
    st.session_state.placeholder = "Please specify your question. E.g. What is a power of attorney?"

# Upload file(s) to saved files directory
def files_upload():
    try:
        shutil.rmtree("saved_files")
    except:
        #Do nothing
        print("Directory does not exist..")

    for uploaded_file in uploaded_files:
        if not os.path.exists("saved_files"): 
            os.makedirs("saved_files")
        #Read the file data
        file_data = uploaded_file.read()
        print(f"File name : {uploaded_file.name}")
        #Define the file path
        save_path = os.path.join("saved_files", uploaded_file.name) 
        # print("save path is : " + save_path)
        # Save the file to the specified directory 
        with open(save_path, "wb") as file: 
            file.write(file_data)

# Define a reset function
def update_placeholder(new_text):
    st.session_state.placeholder = new_text
    st.session_state.user_question1 = ""  # Clear current input

#     # st.write(response.choices[0].message.content)
#     # st.write(f"Prompt Tokens: {response.usage.prompt_tokens}")
#     # st.write(f"Completion Tokens: {response.usage.completion_tokens}")
#     # st.write(f"Total Tokens: {response.usage.total_tokens}")

#     return response.choices[0].message.content

# Get RAG output
def pdf_to_RAG_conversion(user_question):
    # Use DirectoryLoader with custom loader
    loader = DirectoryLoader(
        path="saved_files",  # Your directory containing PDF files
        glob='*.pdf',  # Load all file types recursively
        loader_cls=PyPDFLoader,  # Use your function to choose the loader
        show_progress=True
    )
    documents = loader.load()
    print(f"✅ Loaded {len(documents)} documents.")
    # split documents into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    # for i, doc in enumerate(docs):
    #     print(f"\n--- Chunk {i + 1} ---")
    #     # print(doc.page_content)  # Shows the text content of each chunk
    # print()

    # Initialize OpenAIEmbeddings for Azure  
    embeddings = AzureOpenAIEmbeddings(  
        api_key=AZURE_API_KEY,
        azure_endpoint=AZURE_ENDPOINT,
        model="text-embedding-ada-002",  # Model name  
    )  
    embeddings = OpenAIEmbeddings(api_key="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")

    vectorstore = FAISS.from_documents(documents=docs, embedding=embeddings)  # Ensures it's in-memory only
    retriever = vectorstore.as_retriever(search_kwargs={"k": 30})
    relevant_docs = retriever.invoke(user_question)
    content = "\n\n".join([f"{doc.page_content}\n(Page {doc.metadata.get('page', 'N/A')}, \
            {os.path.basename(doc.metadata.get('source', 'unknown'))})" for doc in relevant_docs]) 
    content += f"\n\n Question: {user_question}"

    #Delete the in-memory database
    # vectorstore._client.delete_collection(vectorstore._collection.name)
    # print(f"Content : {content}")
    return content

#Get legal answer using RAG
def get_legal_answer_using_RAG(question):
    response = AzureOpenAI(
        api_version=AZURE_DEPLOYMENT_ID,
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY
    )
    # response = OpenAI(api_key="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")
    response = response.chat.completions.create(
    messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful and honest legal assistant. " \
                    "Answer the user's question strictly based on all documents content. " 
                    # "If you know the page and filename where the answer derived from, please include a citation in this " \
                    # "exact format : \n\nCitations : \n\n- Page X, filename\n\n" \
                    # "Only include the page number and the filename — no directory paths. "
                    # "If you know the answer, respond with the answer first, followed by a citation in this exact format:\n\n"
                    # "\"(Page X, filename.pdf)\"\n\n"
                    # "Only include the page number and the filename — no directory paths. "
                    # "If you do not know the answer from the document, respond only with:\n"
                    # " I don't know. \n"
                    # "Do not include any citation, page number, or filename in that case."
                    )
            },
            {
                "role": "user", "content": question
            }
        ],
    model="gpt-4o",
    temperature=0,
    max_tokens=4096,
    #     functions=[function], function call not supported in preview
    #     function_call=function_call
    )
    return response.choices[0].message.content

# --- LLM Response ---
def get_legal_answer(question):
    response = AzureOpenAI(
        api_version=AZURE_DEPLOYMENT_ID,
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY
    )

    # response = OpenAI(api_key="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")
    response = response.chat.completions.create(
    messages=[
            {"role": "system", "content": "You are a helpful legal assistant who explains legal topics in plain, simple language."},
            {"role": "user", "content": question}
        ],
    model=AZURE_MODEL,
    temperature=0,
    max_tokens=4096,
    #     functions=[function], function call not supported in preview
    #     function_call=function_call
    )
    return response.choices[0].message.content         

def sanitize_text(text):
    return text.replace('—', '--')  # replace em dash with double dash
    # You can expand this to handle other problematic characters

def normalize_text(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

comparative_legal_analysis = st.sidebar.button("📚 Comparative Legal Analysis")
case_summarization = st.sidebar.button("🧾 Case Summarization ")
element_entries = st.sidebar.button("🧩 Element entries ")
springboard_injunction = st.sidebar.button("🚫 春天的禁令 ")

check_legally_binding_contract = st.sidebar.checkbox("Legally Binding Contract Checker")
# Display only the last 3 messages
for chat in st.session_state.chat_history[-3:]:
    with st.chat_message("user"):
        st.markdown(chat["user"])
    with st.chat_message("assistant"):
        st.markdown(chat["assistant"])# Input with dynamic placeholder

uploaded_files = st.sidebar.file_uploader("Choose an image/pdf...",  type=["pdf"], accept_multiple_files=True)
user_question = st.chat_input(key="Enter your legal question:",
                placeholder=st.session_state.placeholder
            )

# Spacer to push the button visually near the bottom
# st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

# Simulated footer button (just appears under chat)

# Apply custom CSS for beautiful sidebar buttons
st.markdown("""
    <style>
        .sidebar .stButton button {
            width: 100% !important;  /* Make button fill the sidebar width */
            padding: 10px 20px;
            margin-bottom: 10px;
            border-radius: 8px;
            background-color: #4B6CB7;
            color: white;
            font-size: 16px;
            border: none;
            transition: background-color 0.3s ease;
        }
        .sidebar .stButton button:hover {
            background-color: #182848;
            transform: scale(1.03);
        }
        .stSidebar > div:first-child {
            padding-top: 20px;
        }
        .sidebar-title {
            font-size: 20px;
            font-weight: bold;
            color: #4B6CB7;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

if st.sidebar.button("Generate Markdown File"):
    st.success("Markdown File export triggered!")  # Replace with your actual logic
    
    # Open a new Markdown file for writing
    with open("chat_response.md", "w", encoding="utf-8") as md_file:
        for chat in st.session_state.chat_history[-1:]:
            # Format user message
            md_file.write("## **User:**\n")
            md_file.write(f"{normalize_text(chat['user'])}\n\n")

            # Format assistant reply
            md_file.write("## **Assistant:**\n")
            md_file.write(f"{normalize_text(chat['assistant'])}\n\n")
    # pdf = FPDF()
    # pdf.add_page()
    # pdf.set_font("Arial", size=11)

    # # Handle line breaks
    # for line in st.session_state.chat_history[-1:]:
    #     pdf.multi_cell(0, 10, normalize_text(chat["user"]))
    #     pdf.multi_cell(0, 10, normalize_text(chat["assistant"]))
    # # Save PDF
    # pdf.output("chat_response.pdf")

answer = ""
# --- Display Answer ---
if user_question:
    if (len(uploaded_files) > 0):
        if (len(uploaded_files) == 1):  
            with st.spinner("Thinking..."):
                files_upload()
                content = pdf_to_RAG_conversion(user_question)
                answer = get_legal_answer_using_RAG(content)
        else:
            st.error("❌ Please specify one legal case document to compare") 
    else:
        if check_legally_binding_contract:
            with st.spinner("Thinking..."):
                scenario  = """Based on the scenario provided, analyze whether 
                a legally binding contract exists. Your analysis should be structured 
                around the following key elements of contract formation:
                1. Offer
                2. Acceptance
                3. Consideration
                4. Intention to Create Legal Relations
                5. Capacity to Contract:
                6. Certainty and Clarity of Terms:
                7. Legality of Purpose
                After analyzing each element, conclude whether a legally binding contract has been formed. 
                # Clearly explain your reasoning with reference to the facts in the scenario. """
                # At a dinner party, Jane casually tells her friend Mike, "I might sell you my laptop for HK$2,000 
                # if I get a new one next week." Mike responds, "Sure, I’ll take it!" 
                # A week later, Jane decides not to sell.
                print(f"scenario : {scenario}")
                print(f"user_question : {user_question}")
                if scenario is not None and user_question is not None:
                    answer = get_legal_answer(scenario + user_question)
                else:
                    st.error("Please provide both a scenario and a question.")
                
        else:
            with st.spinner("Thinking..."):
                answer = get_legal_answer(user_question)
elif comparative_legal_analysis:
    if (len(uploaded_files) == 2):
        # files_to_images_conversion()
        with st.spinner("Thinking..."):
            user_question = "Please compare these two documents."
            files_upload()
            content = pdf_to_RAG_conversion(COMPARATIVE_LEGAL_ANALYSIS_PROMPT)
            answer = get_legal_answer_using_RAG(content) 
    else: 
        st.error("❌ Please specify two legal case documents to compare")

elif case_summarization:
    if (len(uploaded_files) == 1):
        print(f"Case summarization : {len(uploaded_files)} file")
        # files_to_images_conversion()
        with st.spinner("Thinking..."):
            user_question = "Please summarize this legal document."
            files_upload()
            content = pdf_to_RAG_conversion(CASE_SUMMARIZATION_PROMPT)
            answer = get_legal_answer_using_RAG(content)
            update_placeholder("Please specify your question. E.g. What is a power of attorney?")
    else:
        st.error("❌ Please specify only 1 case document")
        
# elif element_entries:
#     st.switch_page("pages/element_entries.py")
elif springboard_injunction:
    st.switch_page("pages/春天的禁令.py")   
else:
    pass
# Save chat to history
print(f"user : {user_question}")
print(f"assistant : {answer[:10]}")
if answer:
    with st.chat_message("user"):
        st.markdown(user_question)
    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.chat_history.append({"user": user_question, "assistant": answer})
