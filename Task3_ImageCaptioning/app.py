import streamlit as st
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import io

# ==========================================
# 1. Page Configuration & Custom UI Styling
# ==========================================
st.set_page_config(
    page_title="Pro Image Captioning",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Customizing the UI with HTML/CSS injection for a premium look
st.markdown("""
    <style>
    /* Main Background for Dark Theme */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }
    
    /* Styled Title */
    .title-text {
        font-family: 'Helvetica Neue', sans-serif;
        color: #58a6ff;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0px;
    }
    
    /* Caption Box Styling */
    .caption-box {
        background: linear-gradient(145deg, #1f2428, #24292e);
        border-left: 6px solid #58a6ff;
        border-radius: 8px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .caption-title {
        color: #79c0ff;
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .caption-text {
        font-size: 24px;
        font-weight: bold;
        color: #ffffff;
        margin: 0;
        line-height: 1.4;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="title-text">📸 Pro Image Captioning</p>', unsafe_allow_html=True)
st.markdown("### Generate intelligent, context-aware descriptions for your images.")
st.write("Powered by **Salesforce BLIP** and Hugging Face Transformers. Completely free & open-source.")
st.divider()

# ==========================================
# 2. AI Model Loading (Cached for speed)
# ==========================================
@st.cache_resource
def load_model():
    # Load the powerful BLIP base model with its processor
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    return processor, model

with st.spinner("Initializing AI Engine (This might take a minute on first run)..."):
    processor, model = load_model()

# ==========================================
# 3. Sidebar Settings
# ==========================================
with st.sidebar:
    st.header("⚙️ Advanced Settings")
    st.markdown("Customize how the AI generates captions.")
    
    # Conditional text to guide the model
    conditional_prompt = st.text_input(
        "Conditional Prompt (Optional)", 
        placeholder='e.g., "A bright photo of"',
        help="Start the caption with this phrase to guide the AI's generation."
    )
    
    st.divider()
    st.markdown("### 📊 App Info")
    st.info("Batch Processing: **Enabled**\n\nDual Captioning (Short/Detailed): **Enabled**\n\nExport Support: **TXT format**")

# ==========================================
# 4. Main Upload & Processing Section
# ==========================================
# Support for multiple file uploads
uploaded_files = st.file_uploader("Drop multiple images here (.jpg, .png, .jpeg)", 
                                  type=["jpg", "jpeg", "png"], 
                                  accept_multiple_files=True)

if uploaded_files:
    # We will gather all generated captions in this string to enable the user to download it
    all_results_text = "=== Image Captioning Results ===\n\n"
    
    for idx, file in enumerate(uploaded_files):
        st.markdown(f"### 🖼️ Image {idx + 1}: `{file.name}`")
        
        # Open and display the image
        img = Image.open(file)
        
        # Display side-by-side using Streamlit columns
        col_img, col_results = st.columns([1, 1.2]) # Make result column slightly wider
        
        with col_img:
            st.image(img, use_container_width=True, caption="Uploaded Image")
            
            # Extract Image Preprocessing Metadata (Format & Size)
            img_format = img.format if img.format else file.name.split('.')[-1].upper()
            width, height = img.size
            file_size_kb = len(file.getvalue()) / 1024
            
            # Display metadata nicely in an expander
            with st.expander("🔍 Image Preprocessing Metadata", expanded=True):
                st.markdown(f"- **Format:** {img_format}\n"
                            f"- **Dimensions:** {width} x {height} px\n"
                            f"- **File Size:** {file_size_kb:.1f} KB")

        with col_results:
            # Convert to RGB (required for the model, as some PNGs have Alpha/Transparency layers)
            raw_image = img.convert('RGB')
            
            with st.spinner("🧠 AI is generating short & detailed captions..."):
                try:
                    # 1. Preprocess: Prepare input depending on whether user provided a conditional prompt
                    if conditional_prompt.strip():
                        inputs = processor(raw_image, text=conditional_prompt.strip(), return_tensors="pt")
                    else:
                        inputs = processor(raw_image, return_tensors="pt")
                    
                    # 2. Generation - Short Caption
                    # We limit the tokens aggressively for a brief 1-sentence description
                    out_short = model.generate(
                        **inputs, 
                        max_new_tokens=15,
                        num_beams=3
                    )
                    short_caption = processor.decode(out_short[0], skip_special_tokens=True).capitalize()
                    
                    # 3. Generation - Detailed Caption
                    # We force minimum length and use sampling/penalty for a more descriptive result
                    out_detailed = model.generate(
                        **inputs, 
                        max_new_tokens=60,
                        min_new_tokens=25,
                        repetition_penalty=1.5,
                        num_beams=5
                    )
                    detailed_caption = processor.decode(out_detailed[0], skip_special_tokens=True).capitalize()
                    
                    # 4. Display Results in Large, Bold Text
                    all_results_text += f"File: {file.name}\n"
                    all_results_text += f"  [Short]: {short_caption}\n"
                    all_results_text += f"  [Detailed]: {detailed_caption}\n\n"
                    
                    st.markdown(f"""
                    <div class="caption-box">
                        <p class="caption-title">⚡ SHORT CAPTION</p>
                        <p class="caption-text">"{short_caption}"</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="caption-box">
                        <p class="caption-title">📝 DETAILED CAPTION</p>
                        <p class="caption-text">"{detailed_caption}"</p>
                    </div>
                    """, unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error(f"Error analyzing image: {e}")
        
        st.divider() # Separate multiple images

    # ==========================================
    # 5. Global Actions (Download)
    # ==========================================
    st.success("✅ All images processed successfully!")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2: # Center the download button
        st.download_button(
            label="📥 Download All Captions (.txt)",
            data=all_results_text,
            file_name="generated_captions.txt",
            mime="text/plain",
            use_container_width=True
        )
