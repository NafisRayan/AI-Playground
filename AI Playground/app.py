import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from io import BytesIO, TextIOWrapper
import PyPDF2
import docx2txt
import csv
from huggingface_hub import InferenceClient

st.title('👀 AI Playground ')

st.text('Web Scraping with Pandas and Streamlit, Gemini, Mistral, and Phi-3')

Model = st.selectbox("Select your prefered model:", ["GEMINI", "MISTRAL8X", "PHI-3", "Custom Models"])

if Model == "GEMINI":
    tkey = st.text_input("Your Token or API key here:", "")


    # Button to trigger scraping
    # if st.button('Scrape Data'):
    #     if url:
    #         if 'https://' not in url:
    #             url = 'https://' + url
    #         scraped_data = scrape_data(url)
    #         paragraph = ' '.join(scraped_data['Text'].dropna())
    #         st.write(scraped_data)
    #         st.write(paragraph)
        
    #     else:
    #         st.write('Please enter a valid website URL')


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
    
    genai.configure(api_key=tkey)

    def gai(inp):
        return model.generate_content(inp).text

################################################################################################################

else:
    tkey = st.text_input("HuggingFace token here:", "")

    if Model == "MISTRAL8X":
        mkey= "mistralai/Mixtral-8x7B-Instruct-v0.1"
    elif Model == "PHI-3":
        mkey = "microsoft/Phi-3-mini-4k-instruct"
    else:
        mkey = st.text_input("Your HuggingFace Model String here:", "")

    def format_prompt(message, history):
        prompt = ""
        for user_prompt, bot_response in history:
            prompt += f"[INST] {user_prompt} [/INST]"
            prompt += f" {bot_response} "
        prompt += f"[INST] {message} [/INST]"
        return prompt

    def generate(prompt, history=[], temperature=0.9, max_new_tokens=1024, top_p=0.95, repetition_penalty=1.0):
        temperature = float(temperature)
        if temperature < 1e-2:
            temperature = 1e-2
        top_p = float(top_p)

        generate_kwargs = dict(
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
            do_sample=True,
            seed=42,
        )

        formatted_prompt = format_prompt(prompt, history)

        client = InferenceClient(model= mkey, token=tkey)
        stream = client.text_generation(formatted_prompt, **generate_kwargs, stream=True, details=True, return_full_text=False)
        output = ""

        for response in stream:
            output += response.token.text
        
        output = output.replace("<s>", "").replace("</s>", "")
        
        yield output
        return output


    # history = []
    # while True:
    #     user_input = input("You: ")
    #     if user_input.lower() == "off":
    #         break
    #     history.append((user_input, "")) 
    #     for response in generate(user_input, history):
    #         print("Bot:", response)

    def gai(query):
        x=''
        for response in generate(query):
            x+=response
        return x
    
################################################################################################################


# bg image
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
background-image: url(
https://cdn.wallpapersafari.com/41/41/vIdSZT.jpg
);
background-size: cover;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

inp = st.text_input("Enter a prompt and let AI craft stories, poems, code, and more.", "")

# Function to scrape data
def scrape_data(url):
    # Send HTTP request and parse content
    response = requests.get(url)
    # print(response)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Scraping logic - use BeautifulSoup to find and extract various types of content
    texts = [element.text for element in soup.find_all(['p', 'a', 'img'])]
    links = [element.get('href') for element in soup.find_all('a') if element.get('href')]
    images = [element.get('src') for element in soup.find_all('img') if element.get('src')]

    # Ensure all lists are of the same length by padding the shorter ones with None
    max_length = max(len(texts), len(links), len(images))
    texts += [None] * (max_length - len(texts))
    links += [None] * (max_length - len(links))
    images += [None] * (max_length - len(images))

    # Create a DataFrame using pandas for texts, links, and images
    data = {'Text': texts, 'Links': links, 'Images': images}
    df = pd.DataFrame(data)

    # return the processed data
    return df

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

def extract_text_from_csv(file_bytes, encoding='utf-8'):
    # Convert bytes to text using the specified encoding
    file_text = file_bytes.decode(encoding)

    # Use CSV reader to read the content
    csv_reader = csv.reader(TextIOWrapper(BytesIO(file_text.encode(encoding)), encoding=encoding))
    
    # Concatenate all rows and columns into a single text
    text = ""
    for row in csv_reader:
        text += ' '.join(row) + ' '

    return text.replace('\t', ' ').replace('\n', ' ')



url_input = st.checkbox("Use website input")
url = ""
if url_input:
    # Input for the website URL
    url = st.text_input('Enter the website URL (optional): ', '')

file_input = st.checkbox("Use file input")
uploaded_file = None

sp_prompt = ""
prompt_input = st.checkbox("Use special prompt input")
if prompt_input:
    sp_prompt = st.selectbox("Special Prompt (Optional):", [
        "Prompt A: Explain the following with proper details.",
        "Prompt B: Describe the whole thing in a nutshell.",
        "Prompt C: How this can be useful for us?"
    ])

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
            elif file_extension == ".csv":
                uploaded_file = extract_text_from_csv(uploaded_file.getvalue())

            else:
                st.error("Unsupported file type.")

output = ''
previous_responses = []
if st.button("Generate"):
    if tkey == '':
        st.error("Need to input Token or API key.")

    if url:
        if 'https://' not in url:
            url = 'https://' + url
        scraped_data = scrape_data(url)
        paragraph = ' '.join(scraped_data['Text'].dropna())
        # st.write(scraped_data)
        # st.write(paragraph)

        inp = paragraph + ' ' +"Take the given data above, as information and generate a response based on this prompt: " + inp       

    if sp_prompt:
        inp = inp + " " + sp_prompt
    if uploaded_file:
        inp = inp + " " + uploaded_file

    if inp:
        # st.write(inp)
        output = gai(inp)
        st.write(output)

        # # Add response to the list of previous_responses
        # previous_responses.append(output)

        # # Display all previous responses
        # st.subheader("Previous Responses:")
        # for i, response in enumerate(previous_responses, start=1):
        #     st.write(f"{i}. {response}")


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

#st.subheader("[🔗...Visit my GitHub Profile...🔗](https://github.com/NafisRayan)")

# streamlit run app.py
