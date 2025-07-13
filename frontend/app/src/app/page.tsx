"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Check, Loader2 } from "lucide-react";

const steps = [
  "Pulling your medical records",
  "Loading your health data",
  "Analyzing the health data",
  "Generating SMASH FM model",
  "Building your med mirror",
  "Building digital twin for your primary physitian (Dr Samantha Blake, MD)",
];

function BuildProcess({ onComplete }: { onComplete: () => void }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (currentStep < steps.length) {
      setCompletedSteps((prev) => [...prev, currentStep]);
      const timer = setTimeout(() => {
        if (currentStep === steps.length - 1) {
          setIsComplete(true);
          onComplete();
        } else {
          setCurrentStep((prev) => prev + 1);
        }
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [currentStep, onComplete]);

  const getStepStatus = (index: number) => {
    if (completedSteps.includes(index)) return "completed";
    if (index === currentStep) return "current";
    return "pending";
  };

  const progressValue = (completedSteps.length / steps.length) * 100;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold mb-4">Building Your Med Mirror</h2>
        <p className="text-lg text-muted-foreground">
          Please wait while we process your health data...
        </p>
      </div>

      <Card>
        <CardContent className="p-8">
          <div className="space-y-6">
            {steps.map((step, index) => {
              const status = getStepStatus(index);

              return (
                <div key={index} className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    {status === "completed" ? (
                      <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                        <Check className="w-5 h-5 text-white" />
                      </div>
                    ) : status === "current" ? (
                      <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                        <Loader2 className="w-4 h-4 text-primary-foreground animate-spin" />
                      </div>
                    ) : (
                      <div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center">
                        <span className="text-muted-foreground text-sm font-medium">
                          {index + 1}
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="flex-1">
                    <p
                      className={`text-lg font-medium ${
                        status === "completed"
                          ? "text-green-700"
                          : status === "current"
                          ? "text-primary"
                          : "text-muted-foreground"
                      }`}
                    >
                      {step}
                    </p>
                    {status === "current" && (
                      <Badge variant="secondary" className="mt-1">
                        Processing...
                      </Badge>
                    )}
                    {status === "completed" && (
                      <Badge
                        variant="default"
                        className="mt-1 bg-green-100 text-green-800 hover:bg-green-100"
                      >
                        Complete
                      </Badge>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-8">
            <Progress value={progressValue} className="h-2" />
            <p className="text-sm text-muted-foreground mt-2 text-center">
              {completedSteps.length} of {steps.length} steps completed
            </p>
          </div>

          {isComplete && (
            <div className="mt-8 text-center">
              <Card className="bg-green-50 border-green-200 mb-6">
                <CardHeader>
                  <CardTitle className="text-green-800">
                    🎉 Your Med Mirror is Ready!
                  </CardTitle>
                  <CardDescription className="text-green-700">
                    We&apos;ve successfully analyzed your health data and built
                    your personalized medical mirror.
                  </CardDescription>
                </CardHeader>
              </Card>

              <Link href="/dashboard">
                <Button size="lg" className="bg-green-600 hover:bg-green-700">
                  Check out your med mirror
                </Button>
              </Link>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function Home() {
  const [showBuildProcess, setShowBuildProcess] = useState(false);

  const handleStartBuild = () => {
    setShowBuildProcess(true);
  };

  if (showBuildProcess) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background to-muted py-12 px-4">
        <BuildProcess onComplete={() => {}} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold mb-8">Med Mirror</h1>
        <p className="text-xl text-muted-foreground mb-12 max-w-2xl mx-auto">
          Visualize your health journey with personalized insights and
          predictions
        </p>
        <Button
          onClick={handleStartBuild}
          size="lg"
          className="text-xl py-6 px-8"
        >
          Build your med mirror
        </Button>
      </div>
    </div>
  );
}
