import streamlit as st
from openai import OpenAI
from utils import split_text_into_chunks, read_docx, read_pdf, save_to_docx

# --- Streamlit UI Settings ---
st.set_page_config(page_title="📖 Novel Formatter with AI", layout="wide")

st.title("📖 Novel Formatter with AI for Lilou")
st.markdown("**A gift from your amazing BF 😉**")
st.write("""
Upload your manuscript and get a **fully polished and formatted version** 
(APA, Chicago, MLA, or Novel style) with proper headings, spacing, and paragraph breaks.
The text will be corrected for grammar, punctuation, quotations, indentation, and formatting **without changing the meaning or tone**.
""")

# Step-by-step API key instructions
st.markdown("""
**Step 1: Get your OpenAI API Key**  
1. Go to [OpenAI API Keys](https://platform.openai.com/account/api-keys)  
2. Sign in or create an account  
3. Click **Create new secret key**  
4. Name it whatever
5. Copy the key (starts with `sk-`) and keep it safe  

**Step 2: Enter your API Key below**  

You're welcome love! ♥ 
""")

# --- Ask for API Key from User ---
api_key = st.text_input(
    "Enter your OpenAI API Key:",
    type="password",
    placeholder="sk-..."
)

if not api_key:
    st.info("⚠️ Please enter your OpenAI API key to continue.")
    st.stop()

# --- Initialize OpenAI client ---
client = OpenAI(api_key=api_key)

# --- Style Choice ---
style = st.selectbox(
    "Choose formatting style:", 
    ["Novel (Publisher-ready)", "APA", "Chicago", "MLA"]
)

# --- File Upload ---
uploaded_file = st.file_uploader("Upload your manuscript (.docx or .pdf)", type=["docx", "pdf"])

if uploaded_file:
    # Read file
    if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = read_docx(uploaded_file)
    else:
        text = read_pdf(uploaded_file)

    st.success("✅ File uploaded successfully!")
    chunks = list(split_text_into_chunks(text, max_words=3000))
    st.info(f"📑 Split manuscript into {len(chunks)} sections for processing.")

    formatted_sections = []

    if st.button("Process with AI ✨"):
        progress = st.progress(0)
        for i, chunk in enumerate(chunks):
            prompt = f"""
You are a professional editor. Take the following novel section and format it in **{style} style**.
Fix grammar, punctuation, quotations, spacing, indentation, paragraph breaks, and all formatting issues.
Do not change the story, meaning, or tone.
Output should be **ready-to-read, fully formatted**, like a polished novel:

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

        # Save to Word
        output_file = save_to_docx(formatted_sections)
        
        # Button to download fully formatted novel
        with open(output_file, "rb") as f:
            st.download_button(
                "⬇️ Download Fully Formatted Novel",
                f,
                file_name="Formatted_Novel.docx"
            )

        # Display preview
        st.subheader("Preview of Formatted Text (First 2 Sections)")
        st.write("\n\n".join(formatted_sections[:2]))
        st.info("📥 You can download the full formatted novel using the button above.")
