import React, { useRef, useState,useEffect } from 'react'
import "./Video.css"
import { io } from "socket.io-client";

export default function Video() {

    const socket = io("http://localhost:5000");

   const [myStream,setMyStream]=useState()
   const [latency, setLatency] = useState(null);
    const [receivedFrame, setReceivedFrame] = useState(null);

   const currentVideoRef=useRef()

   const handleCallUser =async () => {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: true,
    });

   setMyStream(stream);

   const videoElement = document.createElement('video');
    videoElement.srcObject = stream;

    //const videoElement=currentVideoRef.current

  
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    
    videoElement.addEventListener('loadedmetadata', () => {
      // Adjust canvas size to a smaller dimension (e.g., 320x240)
      canvas.width = 320;
      canvas.height = 240;
  });
  
  videoElement.addEventListener('play', () => {
      const sendFrame = () => {
          // Draw a scaled-down version of the video frame
          context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
          
          // Adjust JPEG compression quality (e.g., 0.5)
          const frame = canvas.toDataURL('image/jpeg', 0.5);
          
         /*  console.log("Frame ", frame); */
          socket.emit('stream', { frame: frame });
          requestAnimationFrame(sendFrame);
      };
  
      sendFrame();
  });
  
  //document.body.appendChild(videoElement);
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
    <div className='outer-container'>
      <div className='heading-container'>
           <h1> Real-Time dehazing of Hazed Video Stream</h1>
           <button  className="stream-btn" onClick={handleCallUser}>Stream Video</button>
           <p>Latency: {latency !== null ? `${latency.toFixed(4)} seconds` : '0.00000 s'}</p>
      </div>
      <div className='video-container'>
        <div className='local vid'>
          <h1> Local Video</h1>
        <video ref={currentVideoRef} autoPlay muted playsInline />
        </div>
        <div className='line'></div>
        <div className='remote vid'>
            <h1> Returned Stream</h1>
            {receivedFrame && <img src={`data:image/jpeg;base64,${receivedFrame}`} alt="Received Frame" style={{ width: '640px', height: '480px' }} />}
        </div>
      </div>
    </div>
  )
}
