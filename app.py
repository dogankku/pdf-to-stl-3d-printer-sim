<!DOCTYPE html>
<html>
<head>
    <title>PDF to STL 3D Printer Sim</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/STLLoader.js"></script>
    <style>
        body { margin: 0; font-family: Arial; }
        #upload { position: absolute; top: 10px; left: 10px; z-index: 100; background: white; padding: 10px; }
        #viewer { width: 100vw; height: 70vh; }
        #printer { height: 30vh; background: #333; position: relative; }
        #download { display: none; }
    </style>
</head>
<body>
    <div id="upload">
        <input type="file" id="fileInput" accept=".pdf,.stl">
        <button onclick="generateModel()">PDF'den STL Üret</button>
        <a id="download" download="model.stl">STL İndir</a>
    </div>
    <div id="viewer"></div>
    <canvas id="printer" width="1200" height="250"></canvas>

<script>
let scene, camera, renderer, model;
const loader = new THREE.STLLoader();

function initViewer() {
    scene = new THREE.Scene(); scene.background = new THREE.Color(0x222222);
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / (window.innerHeight*0.7), 0.1, 1000);
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight*0.7);
    document.getElementById('viewer').appendChild(renderer.domElement);
    
    const light = new THREE.DirectionalLight(0xffffff, 1); light.position.set(1,1,1); scene.add(light);
    const ambient = new THREE.AmbientLight(0x404040); scene.add(ambient);
    camera.position.z = 5;
    animate();
}

function animate() { requestAnimationFrame(animate); if(model) model.rotation.y += 0.005; renderer.render(scene, camera); }

function generateModel() {
    const file = document.getElementById('fileInput').files[0];
    if (!file) return alert('PDF seçin!');
    
    if (file.name.endsWith('.pdf')) {
        // Basit ölçü parse (gerçek app için backend lazım)
        alert('PDF için tam özellik yerel Flask versiyonu kullanın!');
        return;
    } else {
        // STL yükle
        const reader = new FileReader();
        reader.onload = function(e) {
            loader.load(e.target.result, geo => {
                scene.clear(); // Önceki sil
                model = new THREE.Mesh(geo, new THREE.MeshPhongMaterial({color: 0x44ff44}));
                scene.add(model);
                simulatePrint();
            });
        };
        reader.readAsArrayBuffer(file);
    }
}

function simulatePrint() {
    const canvas = document.getElementById('printer');
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#111'; ctx.fillRect(0,0,canvas.width,canvas.height);
    // Yazıcı base
    ctx.fillStyle = '#666'; ctx.fillRect(50,180,300,50);
    
    let layer = 0, maxLayers = 100;
    const printSim = setInterval(() => {
        ctx.fillStyle = `hsl(${layer*3}, 70%, 50%)`;
        ctx.fillRect(100, 180 - layer*0.2, 200, 0.2); // Katman
        layer++;
        if (layer > maxLayers) clearInterval(printSim);
    }, 100);
}

// Başlat
initViewer();
window.addEventListener('resize', () => { camera.aspect = window.innerWidth / (window.innerHeight*0.7); camera.updateProjectionMatrix(); renderer.setSize(window.innerWidth, window.innerHeight*0.7); });
</script>
</body>
</html>
