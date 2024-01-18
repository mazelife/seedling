from __future__ import annotations

import logging
import time
from datetime import datetime
from multiprocessing import Process, Pipe, SimpleQueue
from multiprocessing.connection import Connection
from pathlib import Path
from typing import Sequence, TypedDict

from picamera import PiCamera


logger = logging.getLogger(__name__)


_VIDEO_SENTINEL = b"STOP"
_DATA_SENTINEL = -1


class ProcessData(TypedDict):
    diagnostic_proc: Process
    diagnostic_proc_queue: SimpleQueue[float]
    video_proc: Process
    video_proc_connection: Connection


class Recorder:
    """
    Records a video stream as well as diagnostic info (measured distances) recorded by the motion detector when
    active. The camera recording and diagnostic logging are handled by child processes which are instructed to exit
    when the ``Recorder.stop()`` method is called. This ensures that these operations do not block the parent process
    where motion detection is being handled.
    """

    processes: ProcessData | None = None
    video_file_dir: Path

    def __init__(self, video_file_dir: Path):
        """
        :param video_file_dir: A path to a directory where date-stamped video/diagnostic files should be saved.
        """
        self.video_file_dir = video_file_dir
        self.video_file_dir.mkdir(exist_ok=True)

    @property
    def is_recording(self) -> bool:
        return self.processes is not None

    def send_diagnostic_data(self, distance: float):
        """Send a measured distance to the diagnostic file while recording is taking places."""
        if self.processes:
            self.processes["diagnostic_proc_queue"].put(distance)

    def start(self, current_window: Sequence[float]):
        """
        Start recording video in a separate process.

        :param current_window: The contents of the current moving window of distance data from motion detection
        """
        now_label = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
        video_file = self.video_file_dir / f"{now_label}.h264"  # Write an H.264 video stream
        data_file = self.video_file_dir / f"{now_label}.dat"

        parent_connection, child_connection = Pipe()

        diagnostic_proc_queue: SimpleQueue[float] = SimpleQueue()
        for distance in current_window:
            diagnostic_proc_queue.put(distance)

        video_proc = Process(target=self.record, args=(video_file, child_connection))
        data_proc = Process(target=self.capture_diagnostic_data, args=(data_file, diagnostic_proc_queue))

        self.processes = {
            "diagnostic_proc": data_proc,
            "diagnostic_proc_queue": diagnostic_proc_queue,
            "video_proc": video_proc,
            "video_proc_connection": parent_connection,
        }

        video_proc.start()
        data_proc.start()

    def stop(self):
        """End video recording and instruct child process to exit"""
        if self.processes:
            if self.processes["video_proc"].is_alive():
                self.processes["video_proc_connection"].send(_VIDEO_SENTINEL)

            if self.processes["diagnostic_proc"].is_alive():
                self.processes["diagnostic_proc_queue"].put(_DATA_SENTINEL)

            self.processes["video_proc"].join()
            self.processes["diagnostic_proc"].join()
            self.processes = None

    @staticmethod
    def record(file: Path, connection_to_parent: Connection):
        """Worker process entrypoint for video"""
        start_time = datetime.now()
        logger.info(f'Recording to file "{file}"...')
        camera = PiCamera()
        camera.resolution = (640, 480)
        with file.open("wb") as stream:
            camera.start_recording(stream, format="h264", quality=23)
            while True:
                if connection_to_parent.poll():
                    message: bytes = connection_to_parent.recv()
                    if message == _VIDEO_SENTINEL:
                        stop_time = datetime.now()
                        camera.stop_recording()
                        delta = stop_time - start_time
                        logger.info(f"Video recording stopped after {delta}.")
                        break
                    else:
                        logger.info('Unknown message: "{}". Ignored.'.format(message.decode("utf-8")))
                camera.wait_recording(5)

    @staticmethod
    def capture_diagnostic_data(file: Path, queue: SimpleQueue[int]):
        """Worker process entrypoint for diagnostic data"""
        with file.open("w") as fh:
            while True:
                while not queue.empty():
                    value: int = queue.get()
                    if value == _DATA_SENTINEL:
                        return
                    fh.write(f"{value}\n")
                time.sleep(1)
