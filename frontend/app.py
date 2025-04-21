import streamlit as st
import requests

st.title("Plant Disease Classifier")

uploaded_file = st.file_uploader("Upload a plant image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    if st.button("Check Health"):
        files = {"file": uploaded_file.getvalue()}
        response = requests.post("http://localhost:8000/check-health", files=files)

        if response.status_code == 200:
            result = response.json()
            st.success(result["message"])
        else:
            st.error("Error: Unable to process the image.")