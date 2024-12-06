import os
import streamlit as st
import whisper
import numpy as np
import io
from pydub import AudioSegment
import base64
from referral_letter_generator import ReferralLetterGenerator

# Load Whisper model
def transcribe_audio(file):
    model = whisper.load_model("base")
    audio = AudioSegment.from_file(io.BytesIO(file.read()))
    audio = audio.set_channels(1).set_sample_width(2).set_frame_rate(16000)
    
    # Convert audio to raw audio data for Whisper
    audio_data = np.array(audio.get_array_of_samples(), dtype=np.float32)
    audio_data = audio_data / np.max(np.abs(audio_data))  # Normalize to range [-1, 1]
    
    # Whisper model requires audio in a specific format
    return model.transcribe(audio_data)["text"]


st.title("Medical Referral Letter Generator")

# Create doctor's information if not exists
if not os.path.exists("doctor_info.txt"):
    st.subheader("Doctor's Information")

    name = st.text_input("Name of the doctor")
    designation = st.text_input("Designation")
    contact_info = st.text_input("Contact Information")

    if st.button("Save Doctor Information"):
        with open("doctor_info.txt", "w") as f:
            f.write(f"{name},{designation}\n{contact_info}")
        st.success("Doctor's information saved successfully!")

# Load doctor's info if available
else:
    with open("doctor_info.txt", "r") as f:
        doctor_info, contact_info = f.read().splitlines()

# Audio file upload
st.subheader("Upload Audio File for Transcription")
audio_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a"])

if audio_file:
    with st.spinner("Transcribing audio... Please wait."):
        transcript = transcribe_audio(audio_file)
        
    # Display the transcription in a text area for editing
    edited_transcript = st.text_area("Modify Transcript", transcript, height=200)

    # Generate referral letter
    if st.button("Generate Referral Letter"):
        with st.spinner("Generating Referral Letter... Please wait."):
            referral_generator = ReferralLetterGenerator(edited_transcript, "format.md", doctor_info, contact_info)
            letter = referral_generator.generate_referral_letter()

            st.success("PDF Generated Successfully!")

            # Display and download PDF
            with open("output.pdf", "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
                st.download_button("Download PDF", pdf_file, file_name="referral_letter.pdf", mime="application/pdf")

            # Display PDF inline
            pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
            st.markdown(f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="700" height="900"></iframe>', unsafe_allow_html=True)
