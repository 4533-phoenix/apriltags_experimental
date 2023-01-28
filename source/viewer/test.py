import multiprocessing
import cv2

def worker(port, pipe):
    print("Worker", port)
    camera = cv2.VideoCapture(port, cv2.CAP_DSHOW)
    while True:
        alive, img = camera.read()
        if alive:
            pipe[0].send(img)
        else:
            pipe[0].send(None)

if __name__ == "__main__":
    print("Main")

    workersPipes = []

    for i in [0, 1]:
        pipe = multiprocessing.Pipe()
        workersPipes.append(pipe)
        p = multiprocessing.Process(target=worker, args=(i,pipe))
        p.start()
    
    while True:
        for index, pipe in enumerate(workersPipes):
            img = pipe[1].recv()
            if img is not None:
                cv2.imshow(f"Camera {index}", img)
        
        cv2.waitKey(1)