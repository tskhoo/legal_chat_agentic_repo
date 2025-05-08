import streamlit as st
# from openai import OpenAI
from openai import AzureOpenAI
import os
import shutil
import fitz 
import base64


AZURE_ENDPOINT = "https://khoot-ma1d16zs-eastus2.cognitiveservices.azure.com/"
AZURE_MODEL = "gpt-4o"
AZURE_API_KEY = "8UNdcHUQNEE5uC768eY16kfQVclMMQMuGEM3aECivQvNbDJIKIcaJQQJ99BDACHYHv6XJ3w3AAAAACOGIenh"
AZURE_DEPLOYMENT_ID = "2024-12-01-preview"

COMPREHENSIVE_LEGAL_ANALYSIS_PROMPT = """ You are provided with two legal documents. Please perform a comprehensive analysis that includes the following: 
                        Compare the two documents in terms of their content, legal arguments, and conclusions. 
                        Highlight any notable similarities or differences in the reasoning, 
                        structural organization, and the case authorities cited. 
                        Explain the rationale behind the decisions in each case. What legal 
                        foundations, principles, or precedents were relied upon to reach the outcomes? 
                        Summarize five key facts that are central to the case(s), such as the parties 
                        involved, significant events, legal issues raised, and any material facts that 
                        influenced the judgment. Analyze the judicial reasoning used to reach the 
                        final decision(s). Describe how the judge(s) interpreted and applied the 
                        law to the facts, and outline the logical progression of their analysis. 
                        Identify and explain the case authorities cited in the documents. 
                        Detail how these authorities were used to support or justify the legal reasoning."""

CASE_SUMMARIZATION_PROMPT = """  Please summarize this document in terms of their content, legal arguments, and conclusions. 
                        Highlight any notable similarities or differences in the reasoning, 
                        structural organization, and the case authorities cited. 
                        Explain the rationale behind the decisions in each case. What legal 
                        foundations, principles, or precedents were relied upon to reach the outcomes? 
                        Summarize five key facts that are central to the case(s), such as the parties 
                        involved, significant events, legal issues raised, and any material facts that 
                        influenced the judgment. Analyze the judicial reasoning used to reach the 
                        final decision(s). Describe how the judge(s) interpreted and applied the 
                        law to the facts, and outline the logical progression of their analysis. 
                        Identify and explain the case authorities cited in the documents. 
                        Detail how these authorities were used to support or justify the legal reasoning."""

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


def create_message(system_prompt, user_prompt, base64_images):
    # Create the initial message structure
    message = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_prompt
                }
            ]
        }
    ]
    
    # Add each base64-encoded image to the message
    for base64_image in base64_images:
        message[1]["content"].append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}",
                    "detail": "high"
                }
            }
        )
    
    return message

def pdf_to_images(pdf_path, output_folder, last_num, dpi=150):
    # First time remove everything in the folder (last num = 1 indicates first time)
    if (last_num == 0):
        start_num = 1
        try:
            print("remove tree")
            shutil.rmtree(output_folder)
        except:
            #Do nothing
            print("Directory does not exist..")
    else:
        start_num = last_num
    os.makedirs(output_folder, exist_ok=True)
    pdf_document = fitz.open(pdf_path)
    i = 0
    pages = 2
    for page_num in range(pdf_document.page_count):
        #Limit to 2 pages
        i += 1
        if i > pages:
            break
        # Limit to 2 pages
        # print(page_num)
    
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72)) 
        # pix = page.get_pixmap()
        image_path = os.path.join(output_folder, f'page_{page_num + start_num}.png')
        pix.save(image_path)
        # print(f'Saved: {image_path}')
        last_num = page_num + start_num

    return last_num


# Define a reset function
def update_placeholder(new_text):
    st.session_state.placeholder = new_text
    st.session_state.user_question1 = ""  # Clear current input

# --- Base64 images ---
def get_base64_images(directory):
    base64_images = []
    for filename in os.listdir(directory):
        print(filename)
        print(os.path.join(directory, filename))
        if filename.endswith(".png"):  # You can add more conditions if you have other formats
            with open(os.path.join(directory, filename), 'rb') as img_file:
                base64_image = base64.b64encode(img_file.read()).decode('utf-8')
                base64_images.append(base64_image)
    return base64_images

def invoke_LLM_with_attachment(system_prompt, user_prompt, message_structure):
    response = AzureOpenAI(
        api_version=AZURE_DEPLOYMENT_ID,
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY
    )
    response = response.chat.completions.create(
        messages=message_structure,
        model=AZURE_MODEL,
        temperature=0,
        max_tokens=4096,
        )

    # st.write(response.choices[0].message.content)
    # st.write(f"Prompt Tokens: {response.usage.prompt_tokens}")
    # st.write(f"Completion Tokens: {response.usage.completion_tokens}")
    # st.write(f"Total Tokens: {response.usage.total_tokens}")

    return response.choices[0].message.content
    
# --- LLM Response ---
def get_legal_answer(question):
    response = AzureOpenAI(
        api_version=AZURE_DEPLOYMENT_ID,
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY
    )
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


def files_to_images_conversion():
    # for file in uploaded_files:
    #     st.write(f"File name: {file.name}")
    try:
        print("remove tree")
        shutil.rmtree("saved_files")
        shutil.rmtree("output_images")
    except:
        #Do nothing
        print("Directory does not exist..")

    last_num = 0 # last num is 0 indicates first timer 
    progress_placeholder = st.empty()

    # Show progress bar
    if (len(uploaded_files) == 0):
        interval = 1
    else:
        interval = 1 / len(uploaded_files)
    progress_bar = progress_placeholder.progress(0)
    
    print(f"Interval is {interval}")
    i = 1
    for uploaded_file in uploaded_files:
        # print(uploaded_file.name)
        progress_bar.progress(i * interval)
        # print("last num : " + str(last_num))

        if not os.path.exists("saved_files"): 
            os.makedirs("saved_files")
        
        #Read the file data
        file_data = uploaded_file.read()
        #Define the file path
        save_path = os.path.join("saved_files", uploaded_file.name) 
        # print("save path is : " + save_path)
        # Save the file to the specified directory 
        with open(save_path, "wb") as file: 
            file.write(file_data)
        last_num = pdf_to_images(save_path, "output_images", last_num, dpi=225)
        i += 1
    
    # Clear it (simulate hiding)
    progress_placeholder.empty()
    st.success("✅ Done file processing!")           


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
comprehensive_legal_analysis = st.sidebar.button("📚 Comparative Legal Analysis")
case_summarization = st.sidebar.button("🧾             Case Summarization        ")
element_entries = st.sidebar.button("🧩              Element entries             ")

# Display previous messages
# for i, chat in enumerate(st.session_state.chat_history):
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


answer = ""
# --- Display Answer ---
if user_question:
    if len(uploaded_files):
        files_to_images_conversion()
        with st.spinner("Thinking..."):
            system_prompt = "You are a helpful legal assistant who explains legal topics in plain, simple language."
            directory_path = './output_images/'  # Replace with the path to your directory containing images
            base64_images = get_base64_images(directory_path)
            message_structure = create_message(system_prompt, user_question, base64_images)
            answer = invoke_LLM_with_attachment(system_prompt, user_question, message_structure)
    else:
        with st.spinner("Thinking..."):
            answer = get_legal_answer(user_question)
elif comprehensive_legal_analysis:
    if len(uploaded_files) < 2 or len(uploaded_files) > 2:
        st.error("❌ Please specify 2 case documents to compare")
    else: 
        files_to_images_conversion()
        with st.spinner("Thinking..."):
            system_prompt = "You are a helpful legal assistant who explains legal topics in plain, simple language."
            user_prompt = COMPREHENSIVE_LEGAL_ANALYSIS_PROMPT
            user_question = "Please compare and summarize the two case documents."
            directory_path = './output_images/'  # Replace with the path to your directory containing images
            base64_images = get_base64_images(directory_path)
            message_structure = create_message(system_prompt, user_prompt, base64_images)
            answer = invoke_LLM_with_attachment(system_prompt, user_prompt, message_structure)
elif case_summarization:
    if (len(uploaded_files) > 1 or len(uploaded_files) == 0):
        st.error("❌ Please specify only 1 case document")
    else:
        print(uploaded_files)
        files_to_images_conversion()
        with st.spinner("Thinking..."):
            system_prompt = "You are a helpful legal assistant who explains legal topics in plain, simple language."
            user_prompt = CASE_SUMMARIZATION_PROMPT
            user_question = "Please summarize the case document."
            directory_path = './output_images/'  # Replace with the path to your directory containing images
            base64_images = get_base64_images(directory_path)
            message_structure = create_message(system_prompt, user_prompt, base64_images)
            answer = invoke_LLM_with_attachment(system_prompt, user_prompt, message_structure)
            update_placeholder("Please specify your question. E.g. What is a power of attorney?")
elif element_entries:
    st.switch_page("pages/Element_entries.py")
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
# with st.chat_message("assistant"):
#         st.markdown(chat["assistant"])
# --- Analyze Document ---
# if analyzeDocument and file_ready: 
#     with st.spinner("Thinking..."):
#         system_prompt = "You are a legal expert."
#         user_prompt = user_question
#         directory_path = './output_images/'  # Replace with the path to your directory containing images
#         base64_images = get_base64_images(directory_path)
#         message_structure = create_message(system_prompt, user_prompt, base64_images)
#         invoke_LLM_with_attachment(system_prompt, user_prompt, message_structure)