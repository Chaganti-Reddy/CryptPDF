import json
import requests
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO

# Streamlit App Configuration
st.set_page_config(page_title="CryptPDF", layout="centered")

# Add Snowflake Animation CSS
st.markdown(
    """
    <style>
    /* Remove footer */
    footer {visibility: hidden;}

    /* Snowflake background animation */
    body {
        margin: 0;
        height: 100%;
        background: #1a1a1a;
        overflow: hidden;
    }

    .snowflakes {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
    }

    .snowflake {
        position: absolute;
        color: #ffffff;
        font-size: 1rem;
        opacity: 0.8;
        user-select: none;
        animation: fall linear infinite;
    }

    @keyframes fall {
        0% {
            top: -10%;
            transform: translateX(0);
        }
        100% {
            top: 100%;
            transform: translateX(calc(100vw - 100%));
        }
    }

    </style>

    <script>
    const snowflakesContainer = document.createElement("div");
    snowflakesContainer.classList.add("snowflakes");
    document.body.appendChild(snowflakesContainer);

    function createSnowflake() {
        const snowflake = document.createElement("div");
        snowflake.classList.add("snowflake");
        snowflake.innerText = "❄️"; // Snowflake character
        snowflake.style.left = `${Math.random() * 100}vw`;
        snowflake.style.animationDuration = `${Math.random() * 5 + 5}s`; // Snowfall duration
        snowflake.style.fontSize = `${Math.random() * 1.5 + 0.5}rem`;
        snowflakesContainer.appendChild(snowflake);

        setTimeout(() => {
            snowflake.remove();
        }, 10000); // Matches the max animation duration
    }

    setInterval(createSnowflake, 100);
    </script>
    """,
    unsafe_allow_html=True,
)

# App Title
st.title("❄️ CryptPDF")

st.markdown("""
Upload a PDF file, and **CryptPDF** will automatically detect if it's encrypted or not. 
You can then either remove the password or add a new password.
""")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

def check_encryption_status(uploaded_file):
    """Check if the PDF file is encrypted."""
    try:
        reader = PdfReader(uploaded_file)
        return reader.is_encrypted
    except Exception as e:
        return str(e)

def remove_pdf_password(uploaded_file, password):
    """Remove the password from a PDF file."""
    try:
        reader = PdfReader(uploaded_file)
        if reader.is_encrypted:
            if not reader.decrypt(password):
                raise ValueError("Incorrect password.")
        
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        
        output_stream = BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return output_stream
    except Exception as e:
        return str(e)

def add_pdf_password(uploaded_file, password):
    """Encrypt a PDF file with a password."""
    try:
        reader = PdfReader(uploaded_file)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        writer.encrypt(password)
        
        output_stream = BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return output_stream
    except Exception as e:
        return str(e)

if uploaded_file:
    with st.spinner("Checking file..."):
        encryption_status = check_encryption_status(uploaded_file)
        
    if isinstance(encryption_status, str):
        st.error(f"Error: {encryption_status}")
    else:
        if encryption_status:
            st.info("This file is encrypted. Decrypt it to proceed.")
            action = "Remove Password (Decrypt)"
        else:
            st.info("This file is not encrypted. Encrypt it to add protection.")
            action = "Add Password (Encrypt)"
        
        password = st.text_input(
            f"Enter Password to {'Decrypt' if encryption_status else 'Encrypt'} the PDF",
            type="password"
        )

        if st.button(f"Process: {action}"):
            with st.spinner("Processing..."):
                if encryption_status:  # Decrypt
                    result = remove_pdf_password(uploaded_file, password)
                else:  # Encrypt
                    result = add_pdf_password(uploaded_file, password)
                
                if isinstance(result, BytesIO):
                    st.success(f"{action} successful!")
                    st.download_button(
                        label=f"Download {'Decrypted' if encryption_status else 'Encrypted'} PDF",
                        data=result,
                        file_name="processed.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error(f"Error: {result}")
else:
    st.info("Please upload a PDF file to begin.")
