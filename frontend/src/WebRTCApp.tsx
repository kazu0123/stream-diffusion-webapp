import React, { useState, useEffect, useRef } from "react";

const WebRTCApp: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const [_, setStream] = useState<MediaStream | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  let [generatePrompt, setGeneratePrompt] = useState("");

  useEffect(() => {
    fetch("/load", {
      method: "POST",
      headers: { "Content-Type": "application/json" },

      body: JSON.stringify({
        prompt: generatePrompt,
        model_id: "stabilityai/sd-turbo",
        negative_prompt: "low quality, bad quality, blurry"
      })
    })
      .then((res) => res.json())
      .then(() => setLoading(false))
      .catch((err) => console.error("Failed to load", err));
  }, []);

  const handleScreenCapture = async () => {
    try {
      const screenStream: MediaStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
      setStream(screenStream);
      connectToServer(screenStream);
    } catch (err) {
      console.error("Screen capture failed", err);
    }
  };

  const connectToServer = async (screenStream: MediaStream) => {
    const peerConnection = new RTCPeerConnection();
    screenStream.getTracks().forEach((track: MediaStreamTrack) => {
      peerConnection.addTrack(track, screenStream);
    });

    peerConnection.ontrack = (event) => {
      console.log('ontrack');
      console.log(videoRef.current);
      if (videoRef.current) {
        videoRef.current.srcObject = event.streams[0];
        console.log(videoRef.current.srcObject);
      }
    };

    const offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);

    const response = await fetch("/connect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sdp: offer.sdp, type: offer.type }),
    });

    const answer = await response.json();
    await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
    setConnected(true);
  };

  const submitPrompt = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    await fetch(
      '/update-prompt',
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: generatePrompt })
      }
    )
  }

  return (
    <div className="relative w-screen h-screen bg-gray-900 flex justify-center items-center">
      <video ref={videoRef} autoPlay playsInline className="absolute top-0 left-0 w-full h-full object-cover" />
      <div className="absolute bottom-10 flex gap-4 p-2 bg-gray-500 rounded">
        <button onClick={handleScreenCapture} disabled={loading || connected} className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50">
          画面入力
        </button>
        <form className="contents" onSubmit={submitPrompt}>
          <input type="text" name="prompt" value={generatePrompt} placeholder="生成プロンプトを入力" className="border w-lg px-4 py-2 rounded" disabled={loading} onChange={(e) => setGeneratePrompt(e.target.value)} />
          <button disabled={loading} className="bg-green-500 text-white px-4 py-2 rounded disabled:opacity-50" type="submit">
            送信
          </button>
        </form>
      </div>
    </div>
  );
};

export default WebRTCApp;
