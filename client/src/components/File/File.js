import React, { useEffect, useState } from 'react';
import axios from 'axios';
import "./File.css"
import vidicon from "../../assets/video.png"
import {Circles, CirclesWithBar} from "react-loader-spinner"

const File = () => {
  const [file, setFile] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [loading,setLoading]=useState(false)
  const [uploaded, setUploaded] = useState(false);


  const handleUpload = async (event) => {
    try {
      event.preventDefault();
      setLoading(true)

      const formData = new FormData();
      formData.append('video', file);

      // Use axios to upload the video file to the server
      await axios.post('http://localhost:5000', formData);

      // Display a success message or perform any other actions as needed
     setTimeout(()=>{setLoading(false)},5000)
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

  useEffect(()=>{console.log("Download happening")},[loading])

  return (
    <div className='container'>
      <div className='upload-container'>
          <div className='upload-text'>
             Upload Your hazed video to de-haze
          </div>
          <div className='vid-container'>
            
            <img src={vidicon} width="55px" className='vidicon'/>
            <p> Add video to be dehazed</p>
            
            <div className='upload-box'>
              <label className="custom-file-upload">
              
              <input type="file" accept=".mp4" onChange={(event) => setFile(event.target.files[0])} />
              Browse
              </label>
              <button onClick={handleUpload} disabled={!file} className="custom-file-upload">
              Upload Video
              </button>
            </div>
            {loading ? (
              <div className='loader'>
                <CirclesWithBar
                height="100"
                width="100"
                color="#78efc4"
                wrapperStyle={{}}
                wrapperClass=""
                visible={true}
                outerCircleColor=""
                innerCircleColor=""
                barColor=""
                ariaLabel='circles-with-bar-loading'/>
                </div>
            
          ) : (
            <button onClick={handleDownload} disabled={!uploaded} className="custom-file-upload" style={{ marginTop: "25px" }}>
              Download Processed Video
            </button>
          )}


          </div>
       
         
      </div>
    </div>
  );
};

export default File;
