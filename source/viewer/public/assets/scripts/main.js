"use strict";

// https://threejs.org/docs/#api/en/math/Matrix4

import WebGL from "/assets/scripts/webgl.min.js";

import "/assets/scripts/socketio.min.js";
import "/assets/scripts/three.min.js";

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);

const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);
cube.matrixAutoUpdate = false;

camera.position.z = 5;

function render() {
  renderer.render(scene, camera);
}

if (WebGL.isWebGLAvailable()) {
  const socket = io();

  socket.on("transformations", (data) => {
    cube.matrix.set(...data.robot);
    cube.updateMatrix();
    render();
  });
  render();
} else {
  const warning = WebGL.getWebGLErrorMessage();
  document.getElementById("container").appendChild(warning);
}
