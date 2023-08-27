from __future__ import annotations

import logging
import os
import time
from datetime import datetime
from multiprocessing import Process, Pipe, SimpleQueue
from multiprocessing.connection import Connection
from pathlib import Path
from typing import Sequence

logger = logging.getLogger(__name__)


_VIDEO_SENTINEL = b"STOP"
_DATA_SENTINEL = -1


class Recorder:
    process_communications: tuple[Connection, SimpleQueue] | None = None
    processes: tuple[Process, Process] | None = None
    video_file_dir: Path

    def __init__(self, video_file_dir: Path):
        self.video_file_dir = video_file_dir
        self.video_file_dir.mkdir(exist_ok=True)

    @property
    def is_recording(self) -> bool:
        return self.processes is not None

    def send_diagnostic_data(self, distance: float):
        if self.process_communications:
            _, queue = self.process_communications
            queue.put(distance)

    def start(self, current_window: Sequence[float]):
        now_label = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
        video_file = self.video_file_dir / f"{now_label}.mp4"
        data_file = self.video_file_dir / f"{now_label}.dat"
        parent_connection, child_connection = Pipe()
        diagnostic_data_queue: SimpleQueue[float] = SimpleQueue()
        for distance in current_window:
            diagnostic_data_queue.put(distance)

        self.process_communications = (parent_connection, diagnostic_data_queue)
        recording_proc = Process(target=self.record, args=(video_file, child_connection))
        data_proc = Process(target=self.capture_diagnostic_data, args=(data_file, diagnostic_data_queue))
        self.processes = recording_proc, data_proc
        recording_proc.start()
        data_proc.start()

    def stop(self):
        if self.processes and self.process_communications:
            recording_proc, data_proc = self.processes
            connection_to_recorder, diagnostic_data_queue = self.process_communications

            if recording_proc.is_alive():
                connection_to_recorder.send(_VIDEO_SENTINEL)

            if data_proc.is_alive():
                diagnostic_data_queue.put(_DATA_SENTINEL)

            recording_proc.join()
            data_proc.join()
            self.processes = None
            self.process_communications = None

    @staticmethod
    def record(file: Path, connection_to_parent: Connection):
        start_time = datetime.now()
        logger.info(f'Recording to file "{file}"...')
        with file.open("a"):
            os.utime(str(file), None)
        while True:
            if connection_to_parent.poll():
                message: bytes = connection_to_parent.recv()
                if message == _VIDEO_SENTINEL:
                    stop_time = datetime.now()
                    delta = stop_time - start_time
                    with file.open("w") as fh:
                        fh.write(f"Length: {delta}")
                    logger.info(f"Video recording stopped after {delta}.")
                    break
                else:
                    logger.info('Unknown message: "{}". Ignored.'.format(message.decode("utf-8")))
            time.sleep(1)

    @staticmethod
    def capture_diagnostic_data(file: Path, queue: SimpleQueue[int]):
        with file.open("w") as fh:
            while True:
                while not queue.empty():
                    value: int = queue.get()
                    if value == _DATA_SENTINEL:
                        return
                    fh.write(f"{value}\n")
                time.sleep(1)
