import streamlit as st
import pandas as pd
import json
import os
import tempfile
from PIL import Image
from metadata_extractor import MetadataExtractor

st.set_page_config(page_title="Image Intelligence", layout="wide", page_icon="🔍")

st.title("🔍 Image Detail Extractor & Forensic Tool")
st.markdown("Extract metadata, detect manipulation, calculate entropy, and sanitize images.")

uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png", "tiff", "webp"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Image Preview")
        try:
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)
            
            st.subheader("🛡️ Privacy Tools")
            st.write("Remove all EXIF tags and metadata from the image.")
            if st.button("Strip Metadata"):
                extractor = MetadataExtractor(tmp_path)
                stripped_path = tmp_path + "_stripped" + os.path.splitext(tmp_path)[1]
                success, msg = extractor.strip_metadata(stripped_path)
                if success:
                    st.success("Metadata stripped successfully!")
                    with open(stripped_path, "rb") as f:
                        st.download_button(
                            label="Download Stripped Image",
                            data=f,
                            file_name=f"stripped_{uploaded_file.name}",
                            mime="image/jpeg"
                        )
                else:
                    st.error(msg)
                    
        except Exception as e:
            st.error(f"Could not load image: {e}")
            
    with col2:
        st.subheader("Intelligence Report")
        extractor = MetadataExtractor(tmp_path)
        extractor.filename = uploaded_file.name
        
        metadata = extractor.extract_all()
        
        st.markdown("### 📋 Basic Information")
        basic_df = pd.DataFrame(list(metadata["Basic Info"].items()), columns=["Property", "Value"])
        basic_df["Value"] = basic_df["Value"].astype(str)
        st.table(basic_df)
        
        st.markdown("### 🔐 Security & Forensics")
        sec_df = pd.DataFrame(list(metadata["Security / Forensic Info"].items()), columns=["Property", "Value"])
        sec_df["Value"] = sec_df["Value"].astype(str)
        st.table(sec_df)
        
        exif_info = metadata.get("EXIF Info", {})
        if "Error" not in exif_info:
            st.markdown("### 📷 Camera & Shooting Highlights")
            
            cam = exif_info.get("Camera Info", {})
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**Camera Make:** {cam.get('Make', 'N/A')}")
            with col_b:
                st.write(f"**Camera Model:** {cam.get('Model', 'N/A')}")
                
            highlights = exif_info.get("Highlights", {})
            if highlights:
                st.write("**Shooting Parameters:**")
                h_df = pd.DataFrame(list(highlights.items()), columns=["Parameter", "Value"])
                h_df["Value"] = h_df["Value"].astype(str)
                st.table(h_df)
            
            st.markdown("### 🚨 Editing & Privacy Check")
            sus = exif_info.get("Likely Manipulated", False)
            if sus:
                st.error(f"⚠️ **Software Signature Detected:** {exif_info.get('Software', 'N/A')} - Image may be manipulated.")
            else:
                st.info(f"**Software:** {exif_info.get('Software', 'N/A')}")
                
            risk = exif_info.get("Privacy Risk (GPS Data Found)", False)
            if risk:
                st.error(f"🚨 **PRIVACY RISK:** GPS Location Found: {exif_info.get('GPS Coordinates', 'N/A')}")
                # Interactive Map
                if exif_info.get("Latitude") is not None and exif_info.get("Longitude") is not None:
                    st.markdown("#### 🗺️ Interactive Location Map")
                    map_df = pd.DataFrame({'lat': [exif_info['Latitude']], 'lon': [exif_info['Longitude']]})
                    st.map(map_df, zoom=12, use_container_width=True)
            else:
                st.success("**Safe:** No GPS Coordinates Found.")
                
            st.markdown("### 📄 Export Metadata")
            json_data = json.dumps(metadata, indent=4)
            st.download_button(
                label="Download JSON Report",
                data=json_data,
                file_name=f"{uploaded_file.name}_metadata.json",
                mime="application/json"
            )
            
            with st.expander("Show Raw EXIF Data"):
                raw_exif = exif_info.get("Raw EXIF", {})
                if raw_exif:
                    st.json(raw_exif)
                else:
                    st.write("No EXIF data found.")
        else:
            st.error(exif_info["Error"])
    
    try:
        os.remove(tmp_path)
    except:
        pass
