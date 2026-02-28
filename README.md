🛰️ Image Detail Extractor – Metadata Intelligence Tool

An advanced forensic-style metadata intelligence suite built in Python for deep inspection of image files.

This tool performs structured metadata extraction, GPS intelligence detection, manipulation signature analysis, entropy calculation, and secure sanitization — all through two dedicated user interfaces.

🔎 Overview

Images contain far more information than what is visible to the human eye.

Cameras, smartphones, and editing software embed metadata such as:

Camera model and hardware identifiers

Timestamps

GPS coordinates

Editing software signatures

Compression data

Cryptographic fingerprints

This tool extracts, analyzes, and reports that information in a structured intelligence format.

It is designed for:

Digital forensics

OSINT investigations

Privacy auditing

Cybersecurity research

Educational purposes

🚀 Core Capabilities
1️⃣ Deep EXIF Interrogation

Extracts complete EXIF metadata using Pillow and exifread

Displays camera hardware and capture parameters

Reads hidden metadata fields

2️⃣ GPS Intelligence Detection

Detects embedded latitude & longitude

Converts raw EXIF coordinates to decimal format

Flags privacy exposure risk

Automatically plots location on interactive map (Web version)

3️⃣ Forensic Signature Detection

Detects image manipulation indicators

Identifies software traces (Photoshop, GIMP, etc.)

Scans metadata for suspicious editing artifacts

4️⃣ Hash & Entropy Analysis

Calculates SHA-256 file hash

Measures Shannon entropy for tampering indicators

Provides file fingerprint for verification & integrity checks

5️⃣ Metadata Sanitization (Privacy Tool)

Strips all metadata

Generates clean copy of image

Preserves visual content while removing embedded data

6️⃣ JSON Intelligence Report

Exports full metadata + analysis results

Structured output for SIEM / further processing

🖥️ User Interfaces

The project provides two operational modes.

🌐 Web Intelligence Dashboard (Streamlit)

Interactive forensic dashboard with:

Image preview

Structured metadata tables

GPS mapping (Mapbox)

Downloadable JSON report

Real-time analysis

Run using:

streamlit run web_streamlit.py
🖥️ Desktop Intelligence Client (Tkinter)

Local offline forensic workstation.

Features:

Terminal-style metadata dump

Categorized breakdown

Offline secure analysis

Lightweight interface

Run using:

python gui_tkinter.py
📂 Project Structure
Image-Detail-Extractor/
│
├── metadata_extractor.py   # Core forensic intelligence engine
├── web_streamlit.py        # Web-based dashboard
├── gui_tkinter.py          # Desktop client
├── requirements.txt        # Dependencies
└── README.md               # Project documentation
⚙️ Installation
Requirements

Python 3.8+

pip package manager

Setup

Clone the repository:

git clone https://github.com/avinashdkumar27/image-detail-extractor.git
cd image-detail-extractor

Install dependencies:

pip install -r requirements.txt

Dependencies include:

pillow

exifread

streamlit

pandas

🔐 Security & Ethical Use

This tool is intended strictly for:

Educational use

Security research

Digital forensic analysis

Privacy auditing

⚠️ Ensure you have proper authorization before analyzing any image files. Unauthorized forensic analysis may violate privacy laws.

🧠 Technical Architecture

The core engine:

Parses metadata using Pillow and exifread

Performs cryptographic hashing using hashlib

Calculates entropy using Shannon entropy formula

Detects editing software through metadata field scanning

Converts GPS DMS → Decimal format

Serializes results into structured JSON

Both UI clients call the same backend logic for consistency.

📌 Example Use Cases

Checking whether an image leaked GPS location

Verifying if an image was modified before submission

Generating hash fingerprints for evidence

Cleaning metadata before public upload

Conducting OSINT metadata research