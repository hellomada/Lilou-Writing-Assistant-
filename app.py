import streamlit as st
from openai import OpenAI
from utils import split_text_into_chunks, read_docx, read_pdf, save_to_docx

# --- Streamlit UI ---
st.set_page_config(page_title="📖 Novel Formatter", layout="wide")
st.title("📖 Novel Formatter with AI for Lilou")
st.write(
    """
    Upload your manuscript and get a **fully formatted, polished novel**.
    The AI will:
    - Fix grammar, punctuation, and quotations
    - Correct spacing, paragraph breaks, and indentation
    - Format to professional publishing standards
    - Maintain your original style and tone
    - Offer multiple formatting styles (APA, Chicago, MLA, Novel)
    """
)

# Step-by-step API key instructions
st.markdown("""
**Step 1: Get your OpenAI API Key**  
1. Go to [OpenAI API Keys](https://platform.openai.com/account/api-keys)  
2. Sign in or create an account  
3. Click **Create new secret key**  
4. Copy the key (starts with `sk-`) and keep it safe  

**Step 2: Enter your API Key below**
""")

# API key input
api_key = st.text_input(
    "Enter your OpenAI API Key (keep it private!)",
    type="password",
    placeholder="sk-..."
)

if not api_key:
    st.warning("Please enter your OpenAI API key to proceed.")
    st.stop()

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Formatting style selection
style = st.selectbox(
    "Choose formatting style:", 
    ["APA", "Chicago", "MLA", "Novel (Publisher-ready)"]
)

# Optional advanced options
st.subheader("Advanced Options")
fix_dialogue = st.checkbox("Improve dialogue readability (quotes, speech)", value=True)
fix_tense = st.checkbox("Check verb tense consistency", value=True)
enhance_flow = st.checkbox("Enhance sentence flow and transitions", value=True)

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
            You are a professional novel editor. Take the following section and format it in **{style} style**. 
            Fix grammar, punctuation, quotations, spacing, indentation, paragraph breaks, and all other formatting needed for professional publishing.
            Maintain original meaning, tone, and style. Polish English to a professional level.
            """

            if fix_dialogue:
                prompt += "\n- Improve dialogue readability and consistency."
            if fix_tense:
                prompt += "\n- Check and correct verb tense consistency."
            if enhance_flow:
                prompt += "\n- Enhance sentence flow and transitions between paragraphs."

            prompt += f"\n\nSection:\n{chunk}"

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
            st.download_button(
                "⬇️ Download Final Formatted Novel", 
                f, 
                file_name="Formatted_Novel.docx"
            )

st.info(
    "💡 Tip: Enter your own API key to keep it private and avoid committing secrets. "
    "You can get one for free by signing up at OpenAI and using their free trial credits."
)
