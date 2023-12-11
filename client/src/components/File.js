import React, { useState } from 'react';
import axios from 'axios';

const File = () => {
  const [file, setFile] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
  };

  const handleUpload = async (event) => {
    try {
      event.preventDefault();

      const formData = new FormData();
      formData.append('video', file);

      // Use axios to upload the video file to the server
      const response = await axios.post('http://localhost:5000', formData, { responseType: 'blob' });

      // Create a Blob from the response data
      const blob = new Blob([response.data], { type: 'video/mp4' });

      // Create a URL for the Blob
      const videoUrl = URL.createObjectURL(blob);

      // Set the video URL to be displayed in the HTML5 video element
      setVideoUrl(videoUrl);

    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  return (
    <div>
      <input type="file" accept=".mp4" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={!file}>
        Upload Video
      </button>
      {videoUrl && (
        <div>
          <h2>Processed Video</h2>
          <video controls width="640" height="360">
            <source src={videoUrl} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </div>
      )}
    </div>
  );
};

export default File;
