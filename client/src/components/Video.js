import React, { useRef, useState,useEffect } from 'react'
import { io } from "socket.io-client";

export default function Video() {

    const socket = io("http://localhost:5000");

   const [myStream,setMyStream]=useState()
   const [latency, setLatency] = useState(null);
    const [receivedFrame, setReceivedFrame] = useState(null);

   const currentVideoRef=useRef()

   const handleCallUser =async () => {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: true,
      video: true,
    });

   setMyStream(stream);

   const videoElement = document.createElement('video');
    //videoElement.srcObject = stream;

  
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    
    videoElement.addEventListener('loadedmetadata', () => {
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
    });

    videoElement.addEventListener('play', () => {
        const sendFrame = () => {
            context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
            const frame = canvas.toDataURL('image/jpeg', 0.9);
            console.log("Frame ",frame);
            socket.emit('stream', { frame: frame });
            requestAnimationFrame(sendFrame);
        };

        sendFrame();
    });

    document.body.appendChild(videoElement);
    videoElement.play();
}
useEffect(() => {
    if (currentVideoRef.current && myStream) {
      currentVideoRef.current.srcObject = myStream;
    }
  }, [myStream]);

  useEffect(() => {
    // Listen for the 'response' event from the server
    socket.on('response', data => {
        // Update the state with the received latency and frame data
        setLatency(data.latency);
        setReceivedFrame(data.frame);
    });
     return () => {
      socket.off('response');
  };
}, [socket]); 

  return (
    <div>
      <h1> This is my Stream</h1>
      <button onClick={handleCallUser}>Click here</button>
      <video ref={currentVideoRef} autoPlay muted playsInline />
      <h1> Retured Stream</h1>
      <p>Latency: {latency !== null ? `${latency.toFixed(4)} seconds` : 'Waiting for response...'}</p>
            {receivedFrame && <img src={`data:image/jpeg;base64,${receivedFrame}`} alt="Received Frame" />}
    </div>
  )
}
