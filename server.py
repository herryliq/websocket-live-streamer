import http.server as http
import asyncio
import websockets
import socketserver
import multiprocessing
import cv2
import sys
from datetime import datetime as dt
import builtins

# Keep track of our processes
PROCESSES = []

def log(message):
    print("[LOG] " + str(dt.now()) + " - " + message)

def camera(man):
    # cv2.namedWindow("preview")
    log("Starting camera")
    vc = cv2.VideoCapture(0)

    if vc.isOpened():
        r, f = vc.read()
    else:
        r = False
    
    while r:
        # cv2.imshow("preview", f)
        cv2.waitKey(20)
        r, f = vc.read()
        # f = cv2.resize(f, (640, 480))
        # cv2.putText(f, 
        #             str(time.time()), 
        #             (100, 100), 
        #             cv2.FONT_HERSHEY_SIMPLEX, 
        #             1, 
        #             (255,255,255),
        #             2,
        #             cv2.LINE_AA)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 65]
        man[0] = cv2.imencode('.jpg', f, encode_param)[1]

# HTTP server handler
def server():
    server_address = ('0.0.0.0', 8000)
    if sys.version_info[1] < 7:
        class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.HTTPServer):
            pass
        httpd = ThreadingHTTPServer(server_address, http.SimpleHTTPRequestHandler)
    else:
        httpd = http.ThreadingHTTPServer(server_address, http.SimpleHTTPRequestHandler)
    log("Server started")
    httpd.serve_forever()

def socket(man):
    # Will handle our websocket connections
    async def handler(websocket, path):
        log("Socket opened")
        try:
            while True:
                # try:
                #     x = await asyncio.wait_for(websocket.recv(), 0.010)
                #     print(x)
                # except asyncio.TimeoutError:
                #     pass
                await asyncio.sleep(0.033) # 30 fps
                await websocket.send(man[0].tobytes())
        except websockets.exceptions.ConnectionClosed:
            log("Socket closed")

    log("Starting socket handler")
    # Create the awaitable object
    start_server = websockets.serve(ws_handler=handler, host='0.0.0.0', port=8585)
    # Start the server, add it to the event loop
    asyncio.get_event_loop().run_until_complete(start_server)
    # Registered our websocket connection handler, thus run event loop forever
    asyncio.get_event_loop().run_forever()


def main():
    # queue = multiprocessing.Queue()
    manager = multiprocessing.Manager()
    lst = manager.list()
    lst.append(None)
    # Replace our print function
    # builtins.print = logger().print
    # Host the page, creating the server
    http_server = multiprocessing.Process(target=server)
    # Set up our websocket handler
    socket_handler = multiprocessing.Process(target=socket, args=(lst,))
    # Set up our camera
    camera_handler = multiprocessing.Process(target=camera, args=(lst,))
    # Add 'em to our list
    PROCESSES.append(camera_handler)
    PROCESSES.append(http_server)
    PROCESSES.append(socket_handler)
    for p in PROCESSES:
        p.start()
    # Wait forever
    while True:
        pass

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        for p in PROCESSES:
            p.terminate()