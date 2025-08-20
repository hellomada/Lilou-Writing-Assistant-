import streamlit as st
from openai import OpenAI
from utils import split_text_into_chunks, read_docx, read_pdf, save_to_docx

# --- Load API key from secrets.txt ---
def load_api_key():
    with open("secrets.txt", "r") as f:
        return f.read().strip()  # just the raw key, no "OPENAI_KEY=" prefix

api_key = load_api_key()

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# --- Streamlit UI ---
st.set_page_config(page_title="Novel Formatter", layout="wide")
st.title("📖 Novel Formatter with AI for Lilou")
st.write("Upload your manuscript and get a fully formatted version (APA, Chicago, Novel style, etc.).")

# Style choice
style = st.selectbox("Choose formatting style:", ["APA", "Chicago", "MLA", "Novel (Publisher-ready)"])

# File upload
uploaded_file = st.file_uploader("Upload your manuscript (.docx or .pdf)", type=["docx", "pdf"])

if uploaded_file:
    if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = read_docx(uploaded_file)
    else:
        text = read_pdf(uploaded_file)

    st.write("✅ File uploaded. Splitting into sections...")
    chunks = list(split_text_into_chunks(text, max_words=3000))
    st.write(f"📑 Split into {len(chunks)} sections.")

    formatted_sections = []

    if st.button("Process with AI ✨"):
        progress = st.progress(0)
        for i, chunk in enumerate(chunks):
            prompt = f"""
            You are a professional editor. Take the following novel section and format it in **{style} style**. 
            Fix grammar, punctuation, quotations, spacing, indentation, paragraph breaks, 
            and all other formatting needed for professional publishing. 
            DO NOT change the meaning, wording, or tone. Just polish the English.

            Section:
            {chunk}
            """

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )
                formatted_text = response.choices[0].message.content
            except Exception as e:
                formatted_text = f"[Error processing section {i+1}: {e}]"

            formatted_sections.append(formatted_text)
            progress.progress((i + 1) / len(chunks))

        st.success("✅ Formatting complete!")

        output_file = save_to_docx(formatted_sections)
        with open(output_file, "rb") as f:
            st.download_button("⬇️ Download Final Formatted Novel", f, file_name="Formatted_Novel.docx")
