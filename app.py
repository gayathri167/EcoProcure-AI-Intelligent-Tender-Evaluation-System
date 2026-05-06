"""
**EcoProcure AI** is an intelligent system that automates tender evaluation for plastic waste management.

### 🔄 How it Works:
1. 📄 Upload Tender Document (PDF)
2. 🤖 Extract requirements using NLP (capacity, experience)
3. 🧾 Enter bidder details
4. 📊 Evaluate bidders using scoring logic
5. 🏆 Rank bidders and highlight the best one
6. 🚩 Detect unrealistic or fraudulent claims

### ⚙️ Technologies Used:
- Python
- Streamlit (UI)
- NLP (Regex-based extraction)
- Data Analysis & Visualization

### 🎯 Purpose:
To make government procurement faster, transparent, and data-driven.
"""
import streamlit as st
import pdfplumber
import re
import pandas as pd
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="EcoProcure AI", page_icon="♻️", layout="wide")

# Custom UI styling
st.markdown("""
    <style>
    .main {background-color: #f5f7fa;}
    .stButton>button {background-color: green; color: white;}
    .highlight {color: green; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

st.title("♻️ EcoProcure AI – Tender Analyzer")

# Upload file
uploaded_file = st.file_uploader("📄 Upload Tender Document (PDF)", type="pdf")

# Extract text safely
def extract_text_from_pdf(file):
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        st.error("Invalid or unsupported PDF file.")
        return ""
    return text

# Extract requirements
def extract_requirements(text):
    capacity = None
    experience = None

    cap_match = re.search(r'(\d+)\s*(tons|tonnes)', text.lower())
    if cap_match:
        capacity = int(cap_match.group(1))

    exp_match = re.search(r'(\d+)\s*(years)', text.lower())
    if exp_match:
        experience = int(exp_match.group(1))

    return capacity, experience


# MAIN FLOW
if uploaded_file is not None:

    st.success("✅ File uploaded successfully!")

    extracted_text = extract_text_from_pdf(uploaded_file)

    capacity, experience = extract_requirements(extracted_text)

    st.subheader("📌 Extracted Requirements")
    st.write(f"♻️ Capacity: {capacity} tons" if capacity else "Capacity not found")
    st.write(f"📅 Experience: {experience} years" if experience else "Experience not found")

    st.divider()

    # Bidder input
    st.subheader("🧾 Enter Bidder Details")

    bidder_name = st.text_input("Bidder Name")
    bidder_capacity = st.number_input("Recycling Capacity (tons)", min_value=0)
    bidder_experience = st.number_input("Years of Experience", min_value=0)
    compliance = st.checkbox("Environmental Compliance Certificate Available")

    if st.button("➕ Add Bidder"):
        if "bidders" not in st.session_state:
            st.session_state.bidders = []

        st.session_state.bidders.append({
            "name": bidder_name,
            "capacity": bidder_capacity,
            "experience": bidder_experience,
            "compliance": compliance
        })

    # Show bidders
    if "bidders" in st.session_state and st.session_state.bidders:
        st.subheader("📋 Bidders List")
        st.write(st.session_state.bidders)

    # Evaluate all bidders
    if st.button("🚀 Evaluate All Bidders"):

        results = []
        detailed_results = []

        for b in st.session_state.bidders:
            score = 0
            reasons = []

            # Capacity
            if capacity is not None and b["capacity"] >= capacity:
                score += 40
                reasons.append("✔ Capacity OK")
            else:
                reasons.append("❌ Capacity low")

            # Experience
            if experience is not None and b["experience"] >= experience:
                score += 30
                reasons.append("✔ Experience OK")
            else:
                reasons.append("❌ Experience low")

            # Compliance
            if b["compliance"]:
                score += 30
                reasons.append("✔ Compliance OK")
            else:
                reasons.append("❌ No compliance")

            # Fraud detection
            if b["capacity"] > 5000:
                reasons.append("🚩 Unrealistic capacity")

            results.append((b["name"], score))
            detailed_results.append({
                "Name": b["name"],
                "Score": score
            })

            # Show explanation
            st.subheader(f"🔍 {b['name']} Evaluation")
            st.write(f"Score: {score}/100")
            for r in reasons:
                st.write(r)

        # Ranking
        results.sort(key=lambda x: x[1], reverse=True)

        st.subheader("🏆 Ranking")
        for r in results:
            st.write(f"{r[0]} → {r[1]}")

        # Top bidder highlight
        top_bidder = results[0]
        st.success(f"🥇 Top Bidder: {top_bidder[0]} with score {top_bidder[1]}")

        # Chart
        df = pd.DataFrame(detailed_results)

        st.subheader("📊 Score Visualization")
        fig, ax = plt.subplots()
        ax.bar(df["Name"], df["Score"])
        ax.set_xlabel("Bidders")
        ax.set_ylabel("Score")
        st.pyplot(fig)