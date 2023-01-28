"use strict";

// https://threejs.org/docs/#api/en/math/Matrix4

import WebGL from "/assets/scripts/webgl.min.js";

import "/assets/scripts/socketio.min.js";
import "/assets/scripts/three.min.js";

let movementSpeed = 0.1;
let keys = [];

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);

const skyboxName = "redeclipse";

function createPathStrings(skyboxName) {
  const basePath = "/assets/images/skybox/";
  const baseFilename = basePath + "/" + skyboxName + "/";
  const fileType = ".png";
  const sides = ["ft", "bk", "up", "dn", "rt", "lf"];
  const pathStings = sides.map(side => {
    return baseFilename + side + fileType;
  });

  return pathStings;
}

function createMaterialArray(skyboxName) {
  const skyboxImagepaths = createPathStrings(skyboxName);
  const materialArray = skyboxImagepaths.map(image => {
    let texture = new THREE.TextureLoader().load(image);

    return new THREE.MeshBasicMaterial({ map: texture, side: THREE.BackSide });
  });
  return materialArray;
}


const renderer = new THREE.WebGLRenderer({
  antialias: true,
  alpha: true
});
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

const materialArray = createMaterialArray(skyboxName);
const skyboxGeo = new THREE.BoxGeometry(500, 500, 500);
const skybox = new THREE.Mesh(skyboxGeo, materialArray);

scene.add(skybox);
scene.add(cube);
scene.add(cube1);
scene.add(plane);

cube.matrixAutoUpdate = false;

cube1.scale.set(0.5, 0.5, 0.5);

plane.lookAt(plane.up);
plane.position.y = -1;

camera.position.set(10, 5, 5);
camera.lookAt(cube.position);

function update() {
  if (keys.includes("w")) {
    camera.translateZ(-movementSpeed);
  }
  if (keys.includes("s")) {
    camera.translateZ(movementSpeed);
  }
  if (keys.includes("a")) {
    camera.translateX(-movementSpeed);
  }
  if (keys.includes("d")) {
    camera.translateX(movementSpeed);
  }
  if (keys.includes("Control")) {
    camera.translateY(-movementSpeed);
  }
  if (keys.includes(" ")) {
    camera.translateY(movementSpeed);
  }
  if (keys.includes("r")) {
    camera.position.set(10, 5, 5);
    camera.lookAt(cube.position);
  }
  if (keys.includes("f")) {
    camera.lookAt(cube.position);
  }
  if (keys.includes("ArrowUp")) {
    movementSpeed = Math.min(0.15, movementSpeed + 0.01);
  }
  if (keys.includes("ArrowDown")) {
    movementSpeed = Math.max(0.05, movementSpeed - 0.01);
  }
}

function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}

if (WebGL.isWebGLAvailable()) {
  const socket = io();

  socket.on("transformations", (data) => {
    cube.matrix.set(...data.robot.matrix);
  });

  window.addEventListener("resize", async (_) => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }, false);

  window.addEventListener("keydown", async (event) => {
    if (!keys.includes(event.key)) {
      keys.push(event.key);
    }
  });

  window.addEventListener("keyup", async (event) => {
    keys = keys.filter((key) => key !== event.key);
  });

  window.addEventListener("beforeunload", async (event) => {
    if (keys.includes("Control")) {
      event.preventDefault();
      event.stopPropagation();
    }
  });

  window.setInterval(update, 1000 / 60);

  animate();
} else {
  const warning = WebGL.getWebGLErrorMessage();
  document.getElementById("container").appendChild(warning);
}
