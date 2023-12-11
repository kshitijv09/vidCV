import React, { useState } from 'react';
import axios from 'axios';


const File = () => {
  const [file, setFile] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);

  const handleUpload = async (event) => {
    try {
      event.preventDefault();

      const formData = new FormData();
      formData.append('video', file);

      // Use axios to upload the video file to the server
      await axios.post('http://localhost:5000', formData);

      // Display a success message or perform any other actions as needed

    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  const handleDownload = async (event) => {
    try {
      event.preventDefault();

      // Use axios to download the processed video file from the server
      const response = await axios.get('http://localhost:5000/getVideo', { responseType: 'blob' });
      

      // Create a Blob from the response data
      const blob = new Blob([response.data], { type: 'video/mp4' });

      console.log(blob)

      // Create a URL for the Blob
      const videoUrl = URL.createObjectURL(blob);

      // Set the video URL to be displayed in the HTML5 video element
      setVideoUrl(videoUrl);

      // Optionally, you can trigger a download using the browser's download attribute
      const downloadLink = document.createElement('a');
      downloadLink.href = videoUrl;
      downloadLink.download = 'processed_video.mp4';
      downloadLink.click();

    } catch (error) {
      console.error('Error downloading file:', error);
    }
  };

  return (
    <div>
      <input type="file" accept=".mp4" onChange={(event) => setFile(event.target.files[0])} />
      <button onClick={handleUpload} disabled={!file}>
        Upload Video
      </button>
     
        <div>
          
          {console.log(videoUrl)}
          
         {/*  <video controls width="640" height="360">
            
            <source src={videoUrl} type="video/mp4" />
            Your browser does not support the video tag.
          </video> */}
          <button onClick={handleDownload}>
            Download Processed Video
          </button>
          
         {/*  <ReactPlayer url={videoUrl} type="video/mp4" /> */}
          {/* <h2>Processed Video</h2> */}
        </div>
      
    </div>
  );
};

export default File;
