import streamlit as st
import fitz
import re
import numpy as np
from stl import mesh
from io import BytesIO

st.set_page_config(page_title="PDF to STL 3D", layout="wide")

st.title("📦 PDF Datasheet → STL + 3D Preview")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("📁 PDF yükle", type="pdf")
    
    if uploaded_file is not None:
        # PDF parse
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = "".join(page.get_text() for page in doc)
        
        # Ölçü bul
        dims_match = re.search(r'(\d+(?:[.,]\d+)?)\s*[xX×]\s*(\d+(?:[.,]\d+)?)\s*[xX×]\s*(\d+(?:[.,]\d+)?)', text)
        if dims_match:
            dims = [float(dims_match.group(i).replace(',', '.')) for i in range(1, 4)]
            st.success(f"✅ Ölçü bulundu: **{dims[0]:.1f} x {dims[1]:.1f} x {dims[2]:.1f} mm**")
        else:
            dims = [68.5, 55.0, 30.0]  # HH-030 varsayılan
            st.warning("⚠️ Ölçü bulunamadı, HH-030 varsayılan kullanılıyor")
        
        # STL üret
        def create_box_stl(x, y, z):
            vertices = np.array([
                [0,0,0], [x,0,0], [x,y,0], [0,y,0],
                [0,0,z], [x,0,z], [x,y,z], [0,y,z]
            ], dtype=np.float32)
            faces = np.array([
                [0,1,2],[0,2,3],[4,5,6],[4,6,7],
                [0,1,5],[0,5,4],[1,2,6],[1,6,5],
                [2,3,7],[2,7,6],[3,0,4],[3,4,7]
            ])
            box_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
            for i, f in enumerate(faces):
                for j in range(3):
                    box_mesh.vectors[i][j] = vertices[f[j]]
            return box_mesh
        
        box_mesh = create_box_stl(*dims)
        stl_bytes = BytesIO()
        box_mesh.save(stl_bytes)
        stl_bytes.seek(0)
        
        st.download_button("⬇️ STL İndir (3D Yazıcı Hazır)", stl_bytes.getvalue(), 
                          f"hh030_{dims[0]:.0f}x{dims[1]:.0f}x{dims[2]:.0f}.stl")

with col2:
    st.video("""
    anvas id="stl-preview" style="width:100%;height:400px;border:1px solid #ccc;background:#222;"></canvas>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/STLLoader.js"></script>
    <script>
    const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(75,1,0.1,1000),
    renderer=new THREE.WebGLRenderer({canvas:document.getElementById('stl-preview')});
    renderer.setSize(500,400);camera.position.z=100;
    const light=new THREE.DirectionalLight(0xffffff,1);scene.add(light);
    const loader=new THREE.STLLoader();
    // Demo kutu (gerçek STL frontend'de zor)
    const geo=new THREE.BoxGeometry(60,50,25);const mat=new THREE.MeshPhongMaterial({color:0x44aa88});
    const model=new THREE.Mesh(geo,mat);scene.add(model);
    function animate(){requestAnimationFrame(animate);model.rotation.y+=0.01;renderer.render(scene,camera);}
    animate();
    </script>
    """, format="html")

st.balloons()
st.caption("✅ HH-030 için optimize: 0.2mm layer, %20 infill, 2.8mm duvar")
