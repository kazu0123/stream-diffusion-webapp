import asyncio
from av import VideoFrame
from aiortc import MediaStreamTrack, VideoStreamTrack

from .stream_diffusion_wrapper import StreamDiffusionWrapper


class Img2ImgVideoStreamTrack(VideoStreamTrack):
  def __init__(self, track: MediaStreamTrack, model: StreamDiffusionWrapper):
    super().__init__()
    self.track = track
    self.model = model

    self.latest_frame = None
    self.frame_available = asyncio.Event()

    asyncio.create_task(self._read_frames())

  async def _read_frames(self):
    while True:
      frame = await self.track.recv()

      self.latest_frame = frame
      self.frame_available.set()

  async def recv(self):
    await self.frame_available.wait()

    frame = self.latest_frame

    self.frame_available.clear()
    if isinstance(frame, VideoFrame):
      input_image = frame.to_image()
      loop = asyncio.get_event_loop()

      output_image = await loop.run_in_executor(None, self.model.img2img, input_image)
      new_frame = VideoFrame.from_image(output_image)
      new_frame.pts = frame.pts
      new_frame.time_base = frame.time_base
      return new_frame
