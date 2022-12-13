import queue
import eventlet
from multiprocessing import Queue
from os import path
import socketio


from .config import Config


def background_loop(q: Queue, sio: socketio.Server, verbosity: int):
    while True:
        try:
            while not q.empty():
                event, data = q.get()
                sio.emit(event, data)
                if verbosity >= 2:
                    print(f"socketio.emit('{event}', {data})")
        except queue.Empty:
            pass
        eventlet.sleep(0.02)


def run_server(config: Config, q: Queue, host: str, port: int, verbosity: int):
    # specifying just local path breaks when run as a module
    root_path = path.abspath(path.dirname(__file__))
    static_files = {
        '/': {'content_type': 'text/html', 'filename': path.join(root_path, 'index.html')},
        '/pfd': {'content_type': 'text/html', 'filename': path.join(root_path, 'pfd.html')},
        '/approach': {'content_type': 'text/html', 'filename': path.join(root_path, 'approach.html')},
        '/static': path.join(root_path, 'static'),
    }

    # TODO: on received `config_request` send `config` event with config dict
    sio = socketio.Server()

    @sio.on('config_request')
    def config_request(_sid, _environ):
        q.put(('config', config.dict()))

    app = socketio.WSGIApp(sio, static_files=static_files)
    eventlet.spawn(background_loop, q, sio, verbosity)
    eventlet.wsgi.server(eventlet.listen((host, port)),
                         app, log_output=verbosity >= 3)
