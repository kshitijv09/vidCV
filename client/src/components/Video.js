import React, { useRef, useState,useEffect } from 'react'
import { io } from "socket.io-client";

export default function Video() {

    const socket = io("http://localhost:5000");

   const [myStream,setMyStream]=useState()
   const currentVideoRef=useRef()

   const handleCallUser =async () => {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: true,
      video: true,
    });

   setMyStream(stream);

   console.log(stream," after conversion", typeof(stream))


   const videoElement = document.createElement('video');
    //videoElement.srcObject = stream;

    console.log("Video Element ",videoElement);

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

    console.log(stream, " after conversion", typeof (stream));
}
useEffect(() => {
    if (currentVideoRef.current && myStream) {
      currentVideoRef.current.srcObject = myStream;
    }
  }, [myStream]);

  return (
    <div>
      <h1> This is my Stream</h1>
      <button onClick={handleCallUser}>Click here</button>
      <video ref={currentVideoRef} autoPlay muted playsInline />
    </div>
  )
}
