import os
import hashlib
import math
import json
from datetime import datetime
from PIL import Image
import exifread

class MetadataExtractor:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.filesize = os.path.getsize(filepath)
        
    def calculate_hash(self):
        sha256_hash = hashlib.sha256()
        with open(self.filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def calculate_entropy(self):
        with open(self.filepath, "rb") as f:
            data = f.read()
        if not data:
            return 0.0
        entropy = 0
        for x in range(256):
            p_x = float(data.count(x)) / len(data)
            if p_x > 0:
                entropy += - p_x * math.log2(p_x)
        return entropy

    def extract_basic_info(self):
        try:
            with Image.open(self.filepath) as img:
                info = {
                    "File Name": self.filename,
                    "File Size (Bytes)": self.filesize,
                    "Format": img.format,
                    "Resolution": f"{img.width} x {img.height}",
                    "Color Mode": img.mode,
                }
                if "dpi" in img.info:
                    info["DPI"] = f"{img.info['dpi']}"
                else:
                    info["DPI"] = "N/A"
                
                stat = os.stat(self.filepath)
                info["System Creation Date"] = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                info["System Modification Date"] = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                
                return info
        except Exception as e:
            return {"Error": f"Could not read basic info: {str(e)}"}

    def _convert_to_degrees(self, value):
        try:
            d = float(value.values[0].num) / float(value.values[0].den)
            m = float(value.values[1].num) / float(value.values[1].den)
            s = float(value.values[2].num) / float(value.values[2].den)
            return d + (m / 60.0) + (s / 3600.0)
        except Exception:
            return None

    def extract_exif(self):
        try:
            with open(self.filepath, "rb") as f:
                tags = exifread.process_file(f, details=True)
            
            exif_data = {}
            gps_data = {}
            camera_info = {}
            software_info = "N/A"
            manipulated = False
            highlights = {}
            
            sus_software = ["photoshop", "gimp", "lightroom", "canva", "premiere"]

            for tag, value in tags.items():
                if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
                    exif_data[tag] = str(value)
                    
                if tag == 'Image Make':
                    camera_info['Make'] = str(value)
                elif tag == 'Image Model':
                    camera_info['Model'] = str(value)
                elif tag == 'Image Software':
                    software_info = str(value)
                    for sus in sus_software:
                        if sus in software_info.lower():
                            manipulated = True
                            break
                            
                if tag in ['EXIF ISOSpeedRatings', 'EXIF ExposureTime', 'EXIF FNumber', 'EXIF FocalLength']:
                    clean_tag = tag.replace('EXIF ', '')
                    highlights[clean_tag] = str(value)

                if "GPS" in tag:
                    gps_data[tag] = value

            lat = None
            lon = None
            if 'GPS GPSLatitude' in gps_data and 'GPS GPSLatitudeRef' in gps_data:
                lat = self._convert_to_degrees(gps_data['GPS GPSLatitude'])
                if gps_data['GPS GPSLatitudeRef'].values == 'S' or gps_data['GPS GPSLatitudeRef'].values == 's':
                    lat = -lat
            if 'GPS GPSLongitude' in gps_data and 'GPS GPSLongitudeRef' in gps_data:
                lon = self._convert_to_degrees(gps_data['GPS GPSLongitude'])
                if gps_data['GPS GPSLongitudeRef'].values == 'W' or gps_data['GPS GPSLongitudeRef'].values == 'w':
                    lon = -lon
            
            gps_coords = f"{lat}, {lon}" if lat is not None and lon is not None else "N/A"
            privacy_risk = lat is not None

            return {
                "Raw EXIF": exif_data,
                "Camera Info": camera_info,
                "Highlights": highlights,
                "Software": software_info,
                "Likely Manipulated": manipulated,
                "GPS Coordinates": gps_coords,
                "Latitude": lat,
                "Longitude": lon,
                "Privacy Risk (GPS Data Found)": privacy_risk
            }
        except Exception as e:
            return {"Error": f"EXIF extraction failed: {str(e)}"}

    def extract_all(self):
        basic_info = self.extract_basic_info()
        exif_info = self.extract_exif()
        hash_val = self.calculate_hash()
        entropy_val = self.calculate_entropy()
        
        return {
            "Basic Info": basic_info,
            "Security / Forensic Info": {
                "SHA-256 Hash": hash_val,
                "File Entropy": f"{entropy_val:.4f} (High entropy may indicate encrypted or heavily compressed data)",
            },
            "EXIF Info": exif_info
        }

    def strip_metadata(self, output_path):
        try:
            with Image.open(self.filepath) as img:
                data = list(img.getdata())
                image_without_exif = Image.new(img.mode, img.size)
                image_without_exif.putdata(data)
                image_without_exif.save(output_path)
            return True, f"Metadata stripped and saved to {output_path}"
        except Exception as e:
            return False, f"Failed to strip metadata: {str(e)}"
