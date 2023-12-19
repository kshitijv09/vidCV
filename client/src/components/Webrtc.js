import React, { useEffect, useRef } from 'react';

const Webrtc = () => {
  const localVideoRef = useRef(null);
  const processedVideoRef = useRef(null);

  useEffect(() => {
    const startWebRTC = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        localVideoRef.current.srcObject = stream;

        const peerConnection = new RTCPeerConnection();

        // Create a data channel
        const dataChannel = peerConnection.createDataChannel('video');

        dataChannel.onopen = () => {
          console.log('Data channel opened');
        };

        dataChannel.onmessage = (event) => {
          // Processed video frames received from the server
          const processedData = event.data;
          displayProcessedVideo(processedData);
        };

        // Add the video track to the connection
        stream.getTracks().forEach(track => {
          peerConnection.addTrack(track, stream);
        });

        // Create an offer and set it as the local description
        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);

        // Send the offer to the server
        sendOfferToServer(peerConnection.localDescription);
      } catch (error) {
        console.error('Error accessing webcam:', error);
      }
    };

    const sendOfferToServer = async (offer) => {
      try {
        const response = await fetch('/offer', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ offer }),
        });
        const data = await response.json();

        // Handle the server's answer if needed
      } catch (error) {
        console.error('Error sending offer to the server:', error);
      }
    };

    const displayProcessedVideo = (processedData) => {
      // Display the processed video frames
      // Implement the display logic for processed video here
      processedVideoRef.current.srcObject = processedData;
    };

    startWebRTC();

    // Cleanup when the component unmounts
    return () => {
      // Add cleanup logic if needed
    };
  }, []);

  return (
    <div>
      <h1>WebRTC Video Processing</h1>
      <div>
        <h2>Local Video Stream</h2>
        <video ref={localVideoRef} autoPlay playsInline muted />
      </div>
      <div>
        <h2>Processed Video Stream</h2>
        <video ref={processedVideoRef} autoPlay playsInline />
      </div>
    </div>
  );
};

export default Webrtc;
