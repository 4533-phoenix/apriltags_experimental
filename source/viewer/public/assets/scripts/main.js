"use strict";

// https://threejs.org/docs/#api/en/math/Matrix4

import STLLoader from "/assets/scripts/stlloader.min.js";

import "/assets/scripts/threexwindow.min.js";
import "/assets/scripts/socketio.min.js";
import "/assets/scripts/three.min.js";

let movementSpeed = 0.1;
let keys = [];

const scene = new THREE.Scene();
// scene.add(new THREE.AxesHelper(5));
const loader = new STLLoader();
const camera = new THREE.PerspectiveCamera(
  90,
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
renderer.setPixelRatio(window.devicePixelRatio);
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

const light = new THREE.SpotLight()
light.position.set(20, 20, 20)


const robotFlipPos = new THREE.Vector3(-1, 1, 1);

// let robot = null;
// loader.load("/assets/models/Simple Robot.stl", (geometry) => {
//   const material = new THREE.MeshPhongMaterial({ color: 0xAAAAAA, specular: 0x111111, shininess: 200 });
//   robot = new THREE.Mesh(geometry, material);
//   robot.scale.set(0.00003937, 0.00003937, 0.00003937);
//   robot.position.set(0, 0, 0);
//   robot.matrixAutoUpdate = false;
//   robot.matrixWorldAutoUpdate = false;
//   scene.add(robot);
// });

const robot_geometry = new THREE.BoxGeometry(1, 1, 1);
const robot_material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
const robot = new THREE.Mesh(robot_geometry, robot_material);
scene.add(robot);

const cube1_geometry = new THREE.BoxGeometry(1, 1, 1);
const cube1_material = new THREE.MeshBasicMaterial({ color: 0xff0000 });
const cube1 = new THREE.Mesh(cube1_geometry, cube1_material);

const plane_geometry = new THREE.PlaneGeometry(10, 10);
const plane_material = new THREE.MeshBasicMaterial({ color: 0x0000ff, side: THREE.DoubleSide });
const plane = new THREE.Mesh(plane_geometry, plane_material);

const grid = new THREE.GridHelper(10, 10);

const materialArray = createMaterialArray(skyboxName);
const skyboxGeo = new THREE.BoxGeometry(500, 500, 500);
const skybox = new THREE.Mesh(skyboxGeo, materialArray);

scene.add(light);
scene.add(cube1);
scene.add(grid);
scene.add(plane);
scene.add(skybox);

cube1.scale.set(0.5, 0.5, 0.1);
cube1.position.set(0, 0.5, 0);

plane.lookAt(plane.up);

camera.position.set(10, 5, 5);
camera.lookAt(cube1.position);

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
    camera.lookAt(robot.position);
  }
  if (keys.includes("f")) {
    camera.lookAt(robot.position);
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

const resize = new THREEx.WindowResize(renderer, camera);
const socket = io();

socket.on("transformations", (data) => {
  if (robot) {
    const robotMatrix = new THREE.Matrix4().set(...data.robot.matrix);
    robotMatrix.decompose(robot.position, robot.quaternion, robot.scale);

    // robot.position.multiply(robotFlipPos);
    // robot.rotation.y = -robot.rotation.y;
    

    // robot.scale.multiply(robotFlipPos);

    // robot.updateMatrix();
    // robot.updateMatrixWorld();
  }
});

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

