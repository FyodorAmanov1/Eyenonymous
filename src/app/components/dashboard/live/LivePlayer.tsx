'use client';

import { useEffect, useRef, useState } from 'react';

type LivePlayerProps = {
  relayHost: string; // e.g. http://localhost:3001
};

export default function LivePlayer({ relayHost }: LivePlayerProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!relayHost || relayHost === '') {
      setError('Stream server not configured');
      setIsLoading(false);
      return;
    }

    let script: HTMLScriptElement | null = null;
    let timeoutId: NodeJS.Timeout;

    const loadStream = () => {
      try {
        script = document.createElement('script');
        script.src = `${relayHost}/client.js`;
        
        script.onerror = () => {
          setError('Failed to load stream client. Make sure the relay server is running.');
          setIsLoading(false);
        };

        script.onload = () => {
          // @ts-ignore
          if (window.loadPlayer && canvasRef.current) {
            try {
              // @ts-ignore
              window.loadPlayer({
                url: `${relayHost.replace('http', 'ws')}/api/stream`,
                canvas: canvasRef.current,
              });
              setError(null);
              setIsLoading(false);
            } catch (err) {
              setError('Failed to initialize video stream');
              setIsLoading(false);
            }
          } else {
            setError('Stream player not available');
            setIsLoading(false);
          }
        };

        // Timeout after 10 seconds
        timeoutId = setTimeout(() => {
          setError('Stream connection timeout. Check if Jetson RTSP server is running.');
          setIsLoading(false);
        }, 10000);

        document.body.appendChild(script);
      } catch (err) {
        setError('Failed to load video stream');
        setIsLoading(false);
      }
    };

    loadStream();

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
      if (script && document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, [relayHost]);

  if (error) {
    return (
      <div className="w-full aspect-video rounded-lg bg-video-bg flex items-center justify-center border border-border">
        <div className="text-center p-6">
          <p className="text-sm text-muted mb-2">⚠️ {error}</p>
          <p className="text-xs text-muted">
            Configure JETSON_RTSP_URL and start the relay server with: <code className="bg-surface-2 px-1 rounded">npm run stream:dev</code>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full aspect-video rounded-lg bg-video-bg border border-border overflow-hidden">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-video-bg/80">
          <div className="text-center">
            <div className="animate-pulse-subtle text-muted text-sm mb-2">Connecting to stream...</div>
            <div className="text-xs text-muted">Waiting for Jetson RTSP feed</div>
          </div>
        </div>
      )}
      <canvas
        ref={canvasRef}
        className="w-full h-full"
      />
    </div>
  );
}