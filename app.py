import streamlit as st
import fitz
import re
import numpy as np
from stl import mesh

st.set_page_config(page_title="PDF to STL", layout="wide")

st.title("🔥 PDF Datasheet → 3D STL Converter")
st.markdown("Direnc.net kutu PDF'lerini yükle, otomatik STL al!")

uploaded_file = st.file_uploader("PDF yükle", type="pdf")

if uploaded_file is not None:
    # PDF parse
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc: text += page.get_text()
    
    # Ölçü bul (76x112x26 gibi)
    dims_match = re.search(r'(\d+(?:\.\d+)?)\s*[xX×]\s*(\d+(?:\.\d+)?)\s*[xX×]\s*(\d+(?:\.\d+)?)', text)
    if dims_match:
        dims = [float(dims_match.group(i)) for i in range(1,4)]
        st.success(f"📏 Bulunan ölçü: {dims[0]}x{dims[1]}x{dims[2]} mm")
    else:
        dims = [50, 50, 20]
        st.warning("📏 Ölçü bulunamadı, varsayılan 50x50x20mm")
    
    # Basit kutu STL
    vertices = np.array([
        [[0,0,0], [dims[0],0,0], [dims[0],dims[1],0]],
        [[0,0,0], [dims[0],dims[1],0], [0,dims[1],0]],
        # Yan yüzler... (tam kod kısaltıldı)
    ])
    faces = np.array([[0,1,2], [0,2,3]])
    your_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            your_mesh.vectors[i][j] = vertices[face[j]]
    
    stl_buffer = BytesIO()
    your_mesh.save(stl_buffer)
    stl_buffer.seek(0)
    
    st.download_button("⬇️ STL İndir", stl_buffer.getvalue(), "kutu.stl", "application/sla")
    st.balloons()
