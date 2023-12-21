import streamlit as st
import google.generativeai as genai

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
#st.markdown(page_bg_img, unsafe_allow_html=True)

# App layout
st.title("👀 AI Playground: Unleash Your Creative Spark!")
st.header("Welcome to your own creative sandbox!")
st.write("Enter a prompt and let AI craft stories, poems, code, and more.")


inp = st.text_input("Input:", "")
# plan to use st.file_uploader
# plan to use st.camera_input

sp_prompt = st.text_input("Special Prompt (Optional): ", "")
# plan to use st.selectbox

x = '''
write a detailed structure chart (dont draw) mentioning dataflow with direction and hierarchy (using 1.1,1.2 for modules 1.1.1,1.1.2 for submodules)  based on the above information. 

use the following format

**1.2 Module: Parse Conversation**
   - Data In: Conversation Record
   - Data Out: Text Description of Conversation

**1.2.1 Submodule: Enhance Audio**
   - Data In: Raw Audio Data
   - Data Out: Noise-Reduced Modified Audio

**1.2.2 Submodule: Convert Audio-to-Text**
   - Data In: Modified Audio
   - Data Out: Raw Text Data

=============================================================
'''

if st.button("Generate"):
    if sp_prompt == 'nriar':
        inp = inp + ' ' + x 
    elif sp_prompt:
        inp = inp + " " + sp_prompt
    if inp:
        output = model.generate_content(inp).text
        st.write(output)
        # plan to use st.download_button
    else:
        st.error("Please enter a prompt to generate text.")

st.subheader("Type 'bye' to exit. 🦴")
st.caption("Nafis Rayan is Always Right")



# Add your logic for saving prompts and generated text here
# Add your logic for exploring different AI models here
# https://www.youtube.com/watch?v=pyWqw5yCNdo
# https://www.youtube.com/watch?v=_Um12_OlGgw
# https://www.youtube.com/watch?v=vIQQR_yq-8I

# streamlit run app.py
