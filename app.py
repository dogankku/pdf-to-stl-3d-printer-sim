import streamlit as st
import fitz
import re
import numpy as np
from stl import mesh
from io import BytesIO

st.set_page_config(page_title="PDF to STL", layout="wide")

st.title("🔥 PDF → STL Converter")
st.markdown("Direnc.net kutu PDF'leri için optimize")

uploaded_file = st.file_uploader("PDF yükle", type="pdf")

if uploaded_file is not None:
    # PDF oku
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = "".join(page.get_text() for page in doc)
    
    # Ölçü parse
    dims_match = re.search(r'(\d+(?:[.,]\d+)?)\s*[xX×]\s*(\d+(?:[.,]\d+)?)\s*[xX×]\s*(\d+(?:[.,]\d+)?)', text)
    dims = [float(dims_match.group(i).replace(',', '.')) for i in range(1,4)] if dims_match else [68.5, 55.0, 30.0]
    
    st.success(f"📏 Ölçüler: **{dims[0]:.1f}×{dims[1]:.1f}×{dims[2]:.1f} mm**")
    
    # STL kutu üret
    vertices = np.array([
        [0,0,0],[dims[0],0,0],[dims[0],dims[1],0],[0,dims[1],0],
        [0,0,dims[2]],[dims[0],0,dims[2]],[dims[0],dims[1],dims[2]],[0,dims[1],dims[2]]
    ], dtype=np.float32)
    
    faces = np.array([
        [0,3,1],[1,3,2],[4,7,5],[5,7,6],[0,1,5],[0,5,4],
        [1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]
    ])
    
    box_mesh = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            box_mesh.vectors[i][j] = vertices[f[j]]
    
    # BytesIO'ya kaydet (hata düzeltildi)
    stl_buffer = BytesIO()
    box_mesh.save_binary(stl_buffer)
    stl_buffer.seek(0)
    
    st.download_button("⬇️ STL İndir", stl_buffer.getvalue(), f"kutu_{dims[0]:.0f}x{dims[1]:.0f}x{dims[2]:.0f}.stl")
    
    # 3D Preview (basit)
    st.markdown("### 🖥️ 3D Önizleme")
    st.components.v1.html("""
    <canvas id="viewer" style="width:100%;height:400px;border:1px solid #ccc;background:#111;"></canvas>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
    const s=new THREE.Scene(),c=new THREE.PerspectiveCamera(75,1.33,0.1,1000),
    r=new THREE.WebGLRenderer({canvas:document.getElementById('viewer')});
    r.setSize(600,400);c.position.z=80;
    const l=new THREE.DirectionalLight(0xffffff);s.add(l);
    const g=new THREE.BoxGeometry(60,50,25),m=new THREE.MeshPhongMaterial({color:0x44ff88});
    const box=new THREE.Mesh(g,m);s.add(box);
    function a(){requestAnimationFrame(a);box.rotation.y+=0.01;r.render(s,c);}a();
    </script>
    """, height=450)

st.balloons()
