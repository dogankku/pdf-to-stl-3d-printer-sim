from flask import Flask, request, send_file, render_template_string
import fitz  # PyMuPDF
import cadquery as cq
import os
import re
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)  # HTML aşağıda

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file.filename.endswith('.pdf'):
        file.save('temp.pdf')
        # Parse dimensions (örnek regex)
        doc = fitz.open('temp.pdf')
        text = ""
        for page in doc: text += page.get_text()
        dims_match = re.search(r'(\d+(?:\.\d+)?)\s*[xX]\s*(\d+(?:\.\d+)?)\s*[xX]\s*(\d+(?:\.\d+)?)', text)
        dims = [float(dims_match.group(i)) for i in range(1,4)] if dims_match else [50,50,20]
        wall = 2.5
        # CadQuery box
        model = (cq.Workplane("XY").box(dims[0], dims[1], dims[2]).faces(">Z").workplane()
                 .rect(dims[0]-wall*2, dims[1]-wall*2).cutThruAll())
        stl_buffer = BytesIO()
        cq.exporters.export(model, stl_buffer, tolerance=0.01)
        stl_buffer.seek(0)
        os.remove('temp.pdf')
        return send_file(stl_buffer, mimetype='application/octet-stream', as_attachment=True, 
                         download_name='model.stl')
    return "Desteklenmiyor", 400

if __name__ == '__main__':
    app.run(debug=True)
  <!DOCTYPE html>
<html>
<head>
    <title>PDF to STL 3D Printer Sim</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/STLLoader.js"></script>
    <style> body { margin: 0; } #viewer { width: 100vw; height: 70vh; } #printer { height: 30vh; background: #333; } </style>
</head>
<body>
    <input type="file" id="fileInput" accept=".pdf">
    <button onclick="processFile()">STL Üret & Simüle Et</button>
    <a id="downloadLink" style="display:none">STL İndir</a>
    <div id="viewer"></div> <!-- Model Viewer -->
    <canvas id="printer"></canvas> <!-- Printer Sim -->

<script>
let scene, camera, renderer, model;
const loader = new THREE.STLLoader();

function initViewer() {
    scene = new THREE.Scene(); scene.background = new THREE.Color(0x222222);
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight * 0.7, 0.1, 1000);
    renderer = new THREE.WebGLRenderer({ antialias: true }); renderer.setSize(window.innerWidth, window.innerHeight*0.7);
    document.getElementById('viewer').appendChild(renderer.domElement);
    const light = new THREE.DirectionalLight(0xffffff, 1); light.position.set(1,1,1); scene.add(light);
    camera.position.z = 5;
    animate();
}

function animate() { requestAnimationFrame(animate); renderer.render(scene, camera); }

function processFile() {
    const file = document.getElementById('fileInput').files[0];
    const formData = new FormData(); formData.append('file', file);
    fetch('/upload', {method: 'POST', body: formData}).then(r => r.blob()).then(blob => {
        const url = URL.createObjectURL(blob);
        loader.load(url, geo => {
            model = new THREE.Mesh(geo, new THREE.MeshPhongMaterial({color: 0x00ff00}));
            scene.add(model);
        });
        document.getElementById('downloadLink').href = url; document.getElementById('downloadLink').style.display = 'block'; document.getElementById('downloadLink').download = 'model.stl';
        simulatePrint();  // Sanal yazıcı
    });
}

function simulatePrint() {
    const canvas = document.getElementById('printer');
    const ctx = canvas.getContext('2d'); canvas.width = window.innerWidth; canvas.height = window.innerHeight*0.3;
    ctx.fillStyle = '#000'; ctx.fillRect(0,0,canvas.width,canvas.height);  // Printer base
    let layer = 0, h = 0.2;  // 0.2mm layers
    const interval = setInterval(() => {
        ctx.fillStyle = `hsl(${layer*2}, 100%, 50%)`;  // Layer color
        ctx.fillRect(100, canvas.height - h*(layer+1), 200, h);  // Extrude sim
        layer++; if (layer > 100) clearInterval(interval);  // 20mm height
    }, 200);
}

// Mouse controls
document.addEventListener('mousemove', onMouseMove);
function onMouseMove(e) { if (model) model.rotation.y += 0.01; }

initViewer();
</script>
</body>
</html>
