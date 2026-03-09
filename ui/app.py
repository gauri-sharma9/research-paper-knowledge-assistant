import streamlit as st
import requests

st.title("📄 Research Paper Knowledge Assistant")

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
