from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack

from .stream_diffusion_wrapper import StreamDiffusionWrapper
from .img2img_video_stream_track import Img2ImgVideoStreamTrack


app = FastAPI()
model: StreamDiffusionWrapper
peerConnection: RTCPeerConnection


@app.post("/load")
async def load(
  model_id = "stabilityai/sd-turbo",
  prompt = "1girl with brown dog hair, thick",
  negative_prompt = "low quality, bad quality, blurry"
):
  global model

  model = StreamDiffusionWrapper(
    model_id_or_path = model_id,
    prompt = prompt,
    negative_prompt = negative_prompt
  )

  print('load')

  return {"model": "loaded"}

@app.post("/connect")
async def connect(sdp_data: dict):
  print('connect')
  global peerConnection

  peerConnection = RTCPeerConnection()

  @peerConnection.listens_to('track')
  def on_track(track: MediaStreamTrack):
    print('track')
    print(track)
    peerConnection.addTrack(Img2ImgVideoStreamTrack(track=track, model=model))

  offer = RTCSessionDescription(sdp_data["sdp"], sdp_data["type"])
  await peerConnection.setRemoteDescription(offer)

  answer = await peerConnection.createAnswer()
  await peerConnection.setLocalDescription(answer)

  return {"sdp": peerConnection.localDescription.sdp, "type": peerConnection.localDescription.type}

from pydantic import BaseModel

class PromptUpdateRequest(BaseModel):
  prompt: str

@app.post('/update-prompt')
async def update_prompt(request: PromptUpdateRequest):
  print('update prompt')
  global model

  model.update_prompt(request.prompt)

  return {"model": "updated"}


app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
