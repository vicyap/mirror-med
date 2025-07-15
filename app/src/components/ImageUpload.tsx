"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Camera, Upload, X, Sparkles } from "lucide-react";
import { VisitData } from "@/hooks/useVisitAPI";

interface ImageUploadProps {
  onImageUpload?: (imageUrl: string) => void;
  smashData: Omit<VisitData, "recommendations">;
}

export default function ImageUpload({
  onImageUpload,
  smashData,
}: ImageUploadProps) {
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [faceAgingResult, setFaceAgingResult] = useState<string | null>(null);
  const [isProcessingAging, setIsProcessingAging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const handleFileSelect = useCallback(
    async (file: File) => {
      if (!file.type.startsWith("image/")) {
        alert("Please select an image file");
        return;
      }

      setIsLoading(true);
      try {
        const reader = new FileReader();
        reader.onload = (e) => {
          const imageUrl = e.target?.result as string;
          setUploadedImage(imageUrl);
          setUploadedFile(file);

          // Cache the image in localStorage
          if (typeof window !== "undefined") {
            localStorage.setItem("cachedImage", imageUrl);
            localStorage.setItem("cachedImageTimestamp", Date.now().toString());
          }

          onImageUpload?.(imageUrl);
          setIsLoading(false);
        };
        reader.readAsDataURL(file);
      } catch (error) {
        console.error("Error uploading image:", error);
        setIsLoading(false);
      }
    },
    [onImageUpload]
  );

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleCameraClick = async () => {
    try {
      setIsLoading(true);
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "environment",
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      });

      setStream(mediaStream);
      setShowCamera(true);

      // Set up video stream and wait for it to be ready
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;

        // Wait for video to be ready
        await new Promise((resolve) => {
          if (videoRef.current) {
            videoRef.current.onloadedmetadata = () => {
              videoRef.current?.play();
              resolve(true);
            };
          }
        });
      }

      setIsLoading(false);
    } catch (error) {
      console.error("Error accessing camera:", error);
      setIsLoading(false);
      // Fallback to file input
      alert("Camera not available. Please use the upload option instead.");
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) {
      console.error("Video or canvas ref not available");
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");

    if (!context) {
      console.error("Canvas context not available");
      return;
    }

    // Check if video has valid dimensions
    if (video.videoWidth === 0 || video.videoHeight === 0) {
      console.error("Video not ready - no dimensions");
      alert("Camera not ready yet. Please wait a moment and try again.");
      return;
    }

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas to blob and process
    canvas.toBlob(
      (blob) => {
        if (blob) {
          const file = new File([blob], "camera-photo.jpg", {
            type: "image/jpeg",
          });
          handleFileSelect(file);
          stopCamera();
        } else {
          console.error("Failed to create blob from canvas");
          alert("Failed to capture photo. Please try again.");
        }
      },
      "image/jpeg",
      0.8
    );
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }
    setShowCamera(false);
  };

  // Set up video stream when camera is shown
  useEffect(() => {
    if (showCamera && stream && videoRef.current) {
      videoRef.current.srcObject = stream;
    }
  }, [showCamera, stream]);

  // Cleanup camera stream on unmount
  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [stream]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleRemoveImage = () => {
    setUploadedImage(null);
    setUploadedFile(null);
    setFaceAgingResult(null);
    if (typeof window !== "undefined") {
      localStorage.removeItem("cachedImage");
      localStorage.removeItem("cachedImageTimestamp");
    }
    onImageUpload?.("");
  };

  const handleFaceAging = async () => {
    if (!uploadedFile) {
      alert("Please upload an image first");
      return;
    }

    setIsProcessingAging(true);
    try {
      // Prepare form data
      const formData = new FormData();
      formData.append("image", uploadedFile);
      formData.append("smash", JSON.stringify(smashData));

      // Call face aging API
      const response = await fetch("/api/face-aging", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.statusText}`);
      }

      const result = await response.json();
      setFaceAgingResult(result.prediction);
    } catch (error) {
      console.error("Face aging error:", error);
      alert("Failed to process face aging. Please try again.");
    } finally {
      setIsProcessingAging(false);
    }
  };

  // Load cached image on component mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      const cachedImage = localStorage.getItem("cachedImage");
      const timestamp = localStorage.getItem("cachedImageTimestamp");

      // Check if cached image is less than 24 hours old
      if (cachedImage && timestamp) {
        const imageAge = Date.now() - parseInt(timestamp);
        const twentyFourHours = 24 * 60 * 60 * 1000;

        if (imageAge < twentyFourHours) {
          setUploadedImage(cachedImage);
          onImageUpload?.(cachedImage);
        } else {
          // Remove expired cached image
          localStorage.removeItem("cachedImage");
          localStorage.removeItem("cachedImageTimestamp");
        }
      }
    }
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Your Digital Twin</CardTitle>
      </CardHeader>
      <CardContent>
        {showCamera ? (
          <div className="space-y-4">
            <div className="relative">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-48 object-cover rounded-lg bg-black"
                onLoadedMetadata={() => {
                  if (videoRef.current) {
                    videoRef.current.play().catch(console.error);
                  }
                }}
                onError={(e) => {
                  console.error("Video error:", e);
                }}
              />
              <canvas ref={canvasRef} className="hidden" />
              {/* Debug info */}
              {process.env.NODE_ENV === "development" && (
                <div className="absolute top-2 left-2 text-xs text-white bg-black bg-opacity-50 p-1 rounded">
                  {videoRef.current?.videoWidth}x{videoRef.current?.videoHeight}
                </div>
              )}
            </div>
            <div className="grid grid-cols-2 gap-2">
              <Button variant="outline" onClick={stopCamera} className="w-full">
                <X className="h-4 w-4 mr-2" />
                Cancel
              </Button>
              <Button onClick={capturePhoto} className="w-full">
                <Camera className="h-4 w-4 mr-2" />
                Capture
              </Button>
            </div>
          </div>
        ) : uploadedImage ? (
          <div className="space-y-4">
            <div className="relative">
              <img
                src={faceAgingResult || uploadedImage}
                alt={faceAgingResult ? "Face aging prediction" : "Uploaded"}
                className="w-full h-48 object-cover rounded-lg"
              />
              <Button
                variant="destructive"
                size="sm"
                className="absolute top-2 right-2"
                onClick={handleRemoveImage}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            {faceAgingResult && (
              <div className="text-center">
                <h4 className="font-medium">You in 10 Years</h4>
                <p className="text-xs text-muted-foreground">
                  AI-generated prediction based on your health data
                </p>
              </div>
            )}

            {/* Face Aging Button */}
            <Button
              onClick={handleFaceAging}
              disabled={isProcessingAging || !uploadedFile}
              className="w-full"
              variant="secondary"
            >
              <Sparkles className="h-4 w-4 mr-2" />
              {isProcessingAging
                ? "Processing..."
                : faceAgingResult
                ? "Regenerate my image based on new data"
                : "Show Me in 10 Years"}
            </Button>

            {/* {!faceAgingResult && (
              <p className="text-xs text-muted-foreground text-center">
                Image cached locally
              </p>
            )} */}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
              <div className="space-y-4">
                <div className="mx-auto w-12 h-12 bg-muted rounded-full flex items-center justify-center">
                  <Upload className="h-6 w-6 text-muted-foreground" />
                </div>
                <div>
                  <p className="text-sm font-medium">Upload a photo</p>
                  <p className="text-xs text-muted-foreground">
                    PNG, JPG up to 10MB
                  </p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <Button
                variant="outline"
                onClick={handleUploadClick}
                disabled={isLoading}
                className="w-full"
              >
                <Upload className="h-4 w-4 mr-2" />
                {isLoading ? "Loading..." : "Upload"}
              </Button>

              <Button
                variant="outline"
                onClick={handleCameraClick}
                disabled={isLoading}
                className="w-full"
              >
                <Camera className="h-4 w-4 mr-2" />
                {isLoading ? "Starting..." : "Camera"}
              </Button>
            </div>
          </div>
        )}

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
        />
      </CardContent>
    </Card>
  );
}
