require('dotenv').config();

const express = require('express');
const enableWs = require('express-ws');
const path = require('path');

const app = express();
enableWs(app);

// RTSP URL from Jetson (required)
const JETSON_RTSP = process.env.JETSON_RTSP_URL || 'rtsp://192.168.0.150:8554/unicast';
const RELAY_PORT = Number(process.env.RELAY_PORT || '3001');

if (!process.env.JETSON_RTSP_URL) {
  console.warn('⚠️  JETSON_RTSP_URL not set, using default:', JETSON_RTSP);
}

const { proxy, scriptUrl } = require('rtsp-relay')(app);

app.ws('/api/stream', proxy({ url: JETSON_RTSP, transport: 'tcp' }));

// Handle client.js - scriptUrl can be a URL or file path
app.get('/client.js', (req, res) => {
  // If scriptUrl is a URL (starts with http/https), redirect to it
  if (scriptUrl.startsWith('http://') || scriptUrl.startsWith('https://')) {
    return res.redirect(scriptUrl);
  }
  
  // Otherwise, treat it as a file path
  const absolutePath = path.isAbsolute(scriptUrl) 
    ? scriptUrl 
    : path.resolve(__dirname, '..', scriptUrl);
  
  res.sendFile(absolutePath);
});

app.listen(RELAY_PORT, () => {
  console.log(`✅ RTSP relay server running on port ${RELAY_PORT}`);
  console.log(`📡 Streaming from: ${JETSON_RTSP}`);
});