from flask import Flask, request, send_file, render_template_string
import fitz
import cadquery as cq
import re
import os
from io import BytesIO

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html><head><title>PDF to STL</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/STLLoader.js"></script>
<style>body{margin:0;}#viewer{width:100vw;height:70vh;}</style></head>
<body>
<input type="file" id="fileInput" accept=".pdf">
<button onclick="process()">STL Üret</button><a id="dl" style="display:none">İndir</a>
<div id="viewer"></div>
<script>
let scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(75,window.innerWidth/(window.innerHeight*0.7),0.1,1000),
renderer=new THREE.WebGLRenderer();renderer.setSize(window.innerWidth,window.innerHeight*0.7);
document.getElementById('viewer').appendChild(renderer.domElement);
camera.position.z=5;const light=new THREE.DirectionalLight(0xffffff);scene.add(light);
function animate(){requestAnimationFrame(animate);renderer.render(scene,camera);}
animate();
function process(){const f=document.getElementById('fileInput').files[0];if(!f)return;
const fd=new FormData();fd.append('file',f);fetch('/convert',{method:'POST',body:fd}).then(r=>r.blob()).then(b=>{
const u=URL.createObjectURL(b);const l=new THREE.STLLoader();l.load(u,g=>{scene.children=[];const m=new THREE.Mesh(g,new THREE.MeshPhongMaterial({color:0x00ff00}));scene.add(m);});document.getElementById('dl').href=u;document.getElementById('dl').style.display='block';document.getElementById('dl').download='model.stl';});}
</script></body></html>
"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/convert', methods=['POST'])
def convert():
    file = request.files['file']
    file.save('temp.pdf')
    doc = fitz.open('temp.pdf')
    text = ''.join(page.get_text() for page in doc)
    dims_match = re.search(r'(\d+(?:\.\d+)?)[xX\s]*(\d+(?:\.\d+)?)[xX\s]*(\d+(?:\.\d+)?)', text)
    dims = [float(dims_match.group(i)) for i in range(1,4)] if dims_match else [50,50,20]
    model = (cq.Workplane("XY").box(dims[0], dims[1], dims[2])
             .faces(">Z").workplane().rect(dims[0]-5,dims[1]-5).cutThruAll())
    stl_buffer = BytesIO()
    cq.exporters.export(model, stl_buffer)
    stl_buffer.seek(0)
    os.remove('temp.pdf')
    return send_file(stl_buffer, mimetype='application/octet-stream', as_attachment=True)

if __name__ == '__main__': app.run(debug=True, port=8501)
