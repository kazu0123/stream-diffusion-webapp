import torch
from PIL import Image
from streamdiffusion import StreamDiffusion
from streamdiffusion.image_utils import postprocess_image

from diffusers.pipelines.stable_diffusion.pipeline_stable_diffusion import StableDiffusionPipeline


class StreamDiffusionWrapper:
  def __init__(
    self,
    model_id_or_path: str = "stabilityai/sd-turbo",
    prompt: str = "1girl with brown dog hair, thick glasses, smiling",
    negative_prompt: str = "low quality, bad quality, blurry, low resolution",
  ):
    self.device = 'mps' if torch.backends.mps.is_available() else 'cpu'

    self.width = 512
    self.height = 512

    try:
      pipe = StableDiffusionPipeline.from_pretrained(
        model_id_or_path,
      ).to(device=self.device)
      
      pipe.to(torch.float16)
      
    except Exception as e:
      print(f"Model load failed: {e}")
      exit()
      
    self.stream = StreamDiffusion(
      pipe=pipe,
      t_index_list=[16, 32],
      torch_dtype=torch.float16,
      width=self.width,
      height=self.height,
      do_add_noise=True,
      frame_buffer_size=1,
      use_denoising_batch=True,
      cfg_type="self"
    )

    self.stream.prepare(
      prompt=prompt,
      negative_prompt=negative_prompt,
      num_inference_steps=50,
      guidance_scale=1.2,
      delta=0.5
    )

  def img2img(self, input_image: Image.Image) -> Image.Image:
    resized = input_image.resize((self.width, self.height))
    preprocessed = self.stream.image_processor.preprocess(resized.convert("RGB"))
    preprocessed = preprocessed.to(device=self.device, dtype=torch.float16)

    output_tensor = self.stream(preprocessed)

    return postprocess_image(
      output_tensor.cpu(),
      output_type="pil"
    )[0]

  def update_prompt(self, prompt: str):
    self.stream.update_prompt(
      prompt=prompt,
    )

  @staticmethod
  def crop_center(img: Image.Image) -> Image.Image:
    orig_width, orig_height = img.size
    length = min(orig_width, orig_height)

    left = (orig_width - length) // 2
    top = (orig_height - length) // 2
    right = left + length
    bottom = top + length

    return img.crop((left, top, right, bottom))
