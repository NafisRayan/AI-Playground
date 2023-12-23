import streamlit as st
import google.generativeai as genai
import os
from io import BytesIO
import PyPDF2
import docx2txt

genai.configure(api_key="AIzaSyDGD5HB6mAH-jnAiXTcibvXNMIt7kaz8q4")

# Set up the model
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
]

model = genai.GenerativeModel(model_name="gemini-pro",
                            generation_config=generation_config,
                            safety_settings=safety_settings)


# bg image
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
background-image: url(
https://huimin-static.oss-cn-hangzhou.aliyuncs.com/hm/a224aeca.gif
);
background-size: calc(100vw + 100vh);
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# App layout
st.title("👀 AI Playground: Unleash Your Creative Spark!")
st.header("Welcome to your own creative sandbox!")
st.write("Enter a prompt and let AI craft stories, poems, code, and more.")



inp = st.text_input("Input:", "")
# plan to use st.file_uploader
# plan to use st.camera_input

sp_prompt = st.text_input("Special Prompt (Optional): ", "")



# Function to extract text from a PDF file
def extract_text_from_pdf(file_bytes):
    pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
    num_pages = len(pdf_reader.pages)

    text = ""
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num] 
        text += page.extract_text() 

    return text.replace('\t', ' ').replace('\n', ' ')

# Function to extract text from a TXT file
def extract_text_from_txt(file_bytes):
    text = file_bytes.decode('utf-8')
    return text

# Function to extract text from a DOCX file
def extract_text_from_docx(file_bytes):
    docx = docx2txt.process(BytesIO(file_bytes))
    return docx.replace('\t', ' ').replace('\n', ' ')




file_input = st.checkbox("Use file input")
uploaded_file = None

if file_input:
    # Add file uploader
    st.write("Upload a PDF, TXT, or DOCX file to extract the text.")
    uploaded_file = st.file_uploader("Choose a file")

    if uploaded_file:
    # Get the file extension
        file_name, file_extension = os.path.splitext(uploaded_file.name)

        if file_extension:
            # Extract text based on the file extension
            if file_extension == ".pdf":
                uploaded_file = extract_text_from_pdf(uploaded_file.getvalue())
            elif file_extension == ".txt":
                uploaded_file = extract_text_from_txt(uploaded_file.getvalue())
            elif file_extension == ".docx":
                uploaded_file = extract_text_from_docx(uploaded_file.getvalue())
            else:
                st.error("Unsupported file type.")

output = ''
if st.button("Generate"):
    if sp_prompt:
        inp = inp + " " + sp_prompt
    if uploaded_file:
        inp = inp + " " + uploaded_file
    if inp:
        output = model.generate_content(inp).text
        st.write(output)

        # Add download button
        if output is not None:
            # filename = 'Generated_Answer.txt'
            # with open(filename, 'w') as f:
            #     f.write(output)

            # Add select box
            ofType = 'txt'
            #ofType = st.selectbox("Chose an output file type: ", ["TXT", "PY", "HTML"])
            st.download_button("Download File", data = output, file_name= f"Generated Answer.{ofType}")
    else:
        st.error("Please enter a prompt to generate text.")

st.subheader("Type 'bye' to exit. 🦴")
st.caption("remember, Nafis Rayan is Always Right")
# Add logic for saving prompts and generated text
# Add logic for exploring different AI models
# https://www.youtube.com/watch?v=pyWqw5yCNdo
# https://www.youtube.com/watch?v=_Um12_OlGgw
# https://www.youtube.com/watch?v=vIQQR_yq-8I

# streamlit run app.py