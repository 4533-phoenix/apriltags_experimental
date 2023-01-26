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

const cube_geometry = new THREE.BoxGeometry(1, 1, 1);
const cube_material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
const cube = new THREE.Mesh(cube_geometry, cube_material);

const cube1_geometry = new THREE.BoxGeometry(1, 1, 1);
const cube1_material = new THREE.MeshBasicMaterial({ color: 0xff0000 });
const cube1 = new THREE.Mesh(cube1_geometry, cube1_material);

const plane_geometry = new THREE.PlaneGeometry(10, 10);
const plane_material = new THREE.MeshBasicMaterial({ color: 0x0000ff, side: THREE.DoubleSide });
const plane = new THREE.Mesh(plane_geometry, plane_material);

scene.add(cube);
scene.add(cube1);
scene.add(plane);

cube.matrixAutoUpdate = false;

cube1.scale.set(0.5, 0.5, 0.5);

plane.lookAt(plane.up);
plane.position.y = -1;

camera.position.set(10, 5, 5);
camera.lookAt(cube.position);

function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}

if (WebGL.isWebGLAvailable()) {
  const socket = io();

  socket.on("transformations", (data) => {
    cube.matrix.set(...data.robot.matrix);
  });

  window.addEventListener("resize", _ => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }, false);

  window.addEventListener("keydown", (event) => {

  });

  animate();
} else {
  const warning = WebGL.getWebGLErrorMessage();
  document.getElementById("container").appendChild(warning);
}
