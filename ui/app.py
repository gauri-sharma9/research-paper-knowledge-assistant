import streamlit as st
import requests
import os

st.title(" Research Paper Knowledge Assistant")

# Upload PDF
uploaded_file = st.file_uploader("Upload a research paper", type=["pdf"])

if uploaded_file is not None:
    save_path = os.path.join("data/papers", uploaded_file.name)

    os.makedirs("data/papers", exist_ok=True)

    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"File uploaded: {uploaded_file.name}")

# Question input
question = st.text_input("Ask a question about the research paper")

# Submit button
if st.button("Submit"):
    if question:
        try:
            response = requests.post(
                "http://127.0.0.1:8000/query",
                json={"question": question}
            )

            st.subheader("Response")
            st.write(response.json())

        except Exception as e:
            st.error(f"Backend connection failed: {e}")
    else:
        st.warning("Please enter a question first.")