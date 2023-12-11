import React, { useEffect, useRef } from 'react';

function Camera() {
  const videoRef = useRef();

  useEffect(() => {
    const videoElement = videoRef.current;

    const streamVideo = async () => {
      try {
        const response = await fetch('http://localhost:5000');
        if (!response.ok) {
          throw new Error('Failed to fetch');
        }

        const reader = response.body.getReader();

        const pump = async () => {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const blob = new Blob([value], { type: 'image/jpeg' });
            const imageUrl = URL.createObjectURL(blob);

            videoElement.src= imageUrl;
          }
        };

        pump();
      } catch (error) {
        console.error('Error:', error);
      }
    };

    streamVideo();
  }, []);

  return (
    <div>
        <h1> Video here</h1>
      <video ref={videoRef} autoPlay muted playsInline />
    </div>
  );
}

export default Camera;
