"use strict";

// https://threejs.org/docs/#api/en/math/Matrix4

import STLLoader from "/assets/scripts/stlloader.min.js";

import "/assets/scripts/threexwindow.min.js";
import "/assets/scripts/socketio.min.js";
import "/assets/scripts/three.min.js";

let movementSpeed = 0.1;
let keys = [];

const scene = new THREE.Scene();
scene.add(new THREE.AxesHelper(5));
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

const plane_geometry = new THREE.PlaneGeometry(10, 10);
const plane_material = new THREE.MeshBasicMaterial({ color: 0x0000ff, side: THREE.DoubleSide });
const plane = new THREE.Mesh(plane_geometry, plane_material);

const grid = new THREE.GridHelper(10, 10);

const materialArray = createMaterialArray(skyboxName);
const skyboxGeo = new THREE.BoxGeometry(500, 500, 500);
const skybox = new THREE.Mesh(skyboxGeo, materialArray);

let fieldObjects = {};
let fieldTypes = {
  "tag": {
    "color": 0xff0000,
    "scale": [0.1, 1, 1]
  }
}

scene.add(light);
scene.add(grid);
scene.add(plane);
scene.add(skybox);

plane.lookAt(plane.up);

camera.position.set(10, 5, 5);
camera.lookAt(plane.position);

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
    camera.lookAt(plane.position);
  }
  if (keys.includes("f")) {
    camera.lookAt(plane.position);
  }
}

function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}

function setFromMatrix(obj, mat) {
  (new THREE.Matrix4().set(...mat)).decompose(obj.position, obj.quaternion, obj.scale);
}

const resize = new THREEx.WindowResize(renderer, camera);
const socket = io();

socket.on("transformations", (data) => {
  Object.entries(data).forEach(([key, value]) => {
    if (key in fieldObjects) {
      setFromMatrix(fieldObjects[key], value);
    } else {
      const type = Object.entries(fieldTypes).find(([key, value]) => key.startsWith(key));
      let cube = null;

      if (type) {
        const geometry = new THREE.BoxGeometry(...type[1].scale);
        const material = new THREE.MeshBasicMaterial({ color: type[1].color });
        cube = new THREE.Mesh(geometry, material);
      } else {
        const geometry = new THREE.BoxGeometry(1, 1, 1);
        const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
        cube = new THREE.Mesh(geometry, material);
      }

      setFromMatrix(cube, value);
      scene.add(cube);
      fieldObjects[key] = cube;
    }
  });

  Object.keys(fieldObjects).forEach((key) => {
    if (!(key in data)) {
      scene.remove(fieldObjects[key]);
      delete fieldObjects[key];
    }
  });
});

window.addEventListener("keydown", async (event) => {
  if (!keys.includes(event.key)) {
    keys.push(event.key);
    event.preventDefault();
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