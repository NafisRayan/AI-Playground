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

# Streamlit app code
st.title('👀 Web Scraping with Pandas and Streamlit and Gemini')

api = st.text_input("Gemenai API key here:", "")

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


sp_prompt = ""
prompt_input = st.checkbox("Use prompt input")
if prompt_input:
    sp_prompt = st.selectbox("Special Prompt (Optional):", ["Option 1", "Option 2", "Option 3"])

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
    if api == '':
        st.error("Need to input Gemenai API key.")

    genai.configure(api_key=api)
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
        output = model.generate_content(inp).text
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
