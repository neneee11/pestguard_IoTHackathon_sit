import { useRef, useState, useCallback, useEffect } from 'react';
import { Camera, RefreshCw, Check } from 'lucide-react';
import { Button } from '@/component/ui/button';

interface CameraCaptureProps {
  onCapture: (imageData: string) => void;
  capturedImage: string | null;
  isVerification?: boolean;
}

export const CameraCapture = ({ onCapture, capturedImage, isVerification = false }: CameraCaptureProps) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: 640, height: 480 }
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsStreaming(true);
        setError(null);
      }
    } catch (err) {
      setError('ไม่สามารถเข้าถึงกล้องได้ กรุณาอนุญาตการใช้งานกล้อง');
      console.error('Camera error:', err);
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (videoRef.current?.srcObject) {
      const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
      tracks.forEach(track => track.stop());
      setIsStreaming(false);
    }
  }, []);

  const capturePhoto = useCallback(() => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      
      if (context) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0);
        const imageData = canvas.toDataURL('image/jpeg', 0.8);
        onCapture(imageData);
        stopCamera();
      }
    }
  }, [onCapture, stopCamera]);

  const retake = useCallback(() => {
    onCapture('');
    startCamera();
  }, [onCapture, startCamera]);

  useEffect(() => {
    if (!capturedImage) {
      startCamera();
    }
    return () => stopCamera();
  }, [capturedImage, startCamera, stopCamera]);

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative w-full max-w-md aspect-[4/3] border-4 border-foreground bg-secondary overflow-hidden shadow-md">
        {/* Face detection overlay */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
          <div className="w-48 h-60 border-4 border-dashed border-foreground/50 rounded-[100px]" />
        </div>
        
        {capturedImage ? (
          <img 
            src={capturedImage} 
            alt="Captured" 
            className="w-full h-full object-cover"
          />
        ) : (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
            />
            {error && (
              <div className="absolute inset-0 flex items-center justify-center bg-secondary">
                <p className="text-destructive text-center px-4 font-mono">{error}</p>
              </div>
            )}
          </>
        )}
        
        {/* Scanning animation for verification mode */}
        {isVerification && isStreaming && !capturedImage && (
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute left-0 right-0 h-1 bg-chart-2 animate-[scan_2s_ease-in-out_infinite]" />
          </div>
        )}
      </div>

      <canvas ref={canvasRef} className="hidden" />

      {capturedImage ? (
        <div className="flex gap-4">
          <Button onClick={retake} variant="outline" size="lg" className="gap-2">
            <RefreshCw className="w-5 h-5" />
            ถ่ายใหม่
          </Button>
          <Button size="lg" className="gap-2" disabled>
            <Check className="w-5 h-5" />
            เลือกภาพนี้
          </Button>
        </div>
      ) : (
        <Button 
          onClick={capturePhoto} 
          disabled={!isStreaming}
          size="lg"
          className="gap-2 min-w-[200px]"
        >
          <Camera className="w-5 h-5" />
          {isVerification ? 'สแกนใบหน้า' : 'ถ่ายภาพ'}
        </Button>
      )}
    </div>
  );
};
