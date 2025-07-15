"use client";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import ImageUpload from "@/components/ImageUpload";
import { useVisitAPI } from "@/hooks/useVisitAPI";
import { ExternalLink } from "lucide-react";
import smashData from "./smash.json";

export default function Dashboard() {
  const {
    isLoading: isVisitLoading,
    improvementData,
    scheduleVisit,
  } = useVisitAPI();

  // Calculate health metrics from smash.json data
  const exerciseRating = smashData.social_history.exercise.rating;
  const sleepRating = smashData.social_history.sleep.rating;
  const alcoholIntake = smashData.social_history.alcohol.rating;

  const handleVisitDoctor = async () => {
    try {
      await scheduleVisit(smashData);
      alert("Visit doctor successfully! Your improvement plan is now showing.");
    } catch (error) {
      console.error("Error calling visit API:", error);
      alert("Failed to schedule visit. Please try again.");
    }
  };

  console.log(improvementData);

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold mb-8">Med Mirror</h1>

        <div className="grid grid-cols-3 gap-8">
          {/* Left Column - Health Metrics Bars */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Health Metrics</CardTitle>
                <CardDescription>
                  Current health parameters from your profile
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Exercise Level */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className="block text-sm font-medium">
                      Exercise Level
                    </label>
                    {improvementData &&
                      improvementData.recommendations.exercise.rating !==
                        exerciseRating && (
                        <span className="text-xs text-green-600 font-medium">
                          +
                          {improvementData.recommendations.exercise.rating -
                            exerciseRating}{" "}
                        </span>
                      )}
                  </div>
                  <div className="relative">
                    {improvementData ? (
                      <>
                        {/* Improvement bar (black) */}
                        <Progress
                          value={
                            improvementData.recommendations.exercise.rating * 10
                          }
                          className="w-full"
                        />
                        {/* Difference overlay (green) */}
                        {improvementData.recommendations.exercise.rating >
                          exerciseRating && (
                          <div
                            className="absolute transition-all duration-700 ease-out bg-green-500"
                            style={{
                              left: `${exerciseRating * 10}%`,
                              width: `${
                                (improvementData.recommendations.exercise
                                  .rating -
                                  exerciseRating) *
                                10
                              }%`,
                              height: "100%",
                              top: 0,
                            }}
                          />
                        )}
                      </>
                    ) : (
                      <Progress
                        value={exerciseRating * 10}
                        className="w-full"
                      />
                    )}
                  </div>
                  <div className="flex justify-between text-xs text-muted-foreground mt-1">
                    <span>0 hrs</span>
                    <span>≥20 hrs</span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {improvementData?.recommendations.exercise.description ||
                      smashData.social_history.exercise.description}
                  </p>
                </div>

                {/* Sleep Hours */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className="block text-sm font-medium">
                      Sleep Hours
                    </label>
                    {improvementData &&
                      improvementData.recommendations.sleep.rating !==
                        sleepRating && (
                        <span className="text-xs text-green-600 font-medium">
                          +
                          {improvementData.recommendations.sleep.rating -
                            sleepRating}{" "}
                        </span>
                      )}
                  </div>
                  <div className="relative">
                    {improvementData ? (
                      <>
                        {/* Improvement bar (black) */}
                        <Progress
                          value={
                            improvementData.recommendations.sleep.rating * 10
                          }
                          className="w-full"
                        />
                        {/* Difference overlay (green) */}
                        {improvementData.recommendations.sleep.rating >
                          sleepRating && (
                          <div
                            className="absolute transition-all duration-700 ease-out bg-green-500"
                            style={{
                              left: `${sleepRating * 10}%`,
                              width: `${
                                (improvementData.recommendations.sleep.rating -
                                  sleepRating) *
                                10
                              }%`,
                              height: "100%",
                              top: 0,
                            }}
                          />
                        )}
                      </>
                    ) : (
                      <Progress value={sleepRating * 10} className="w-full" />
                    )}
                  </div>
                  <div className="flex justify-between text-xs text-muted-foreground mt-1">
                    <span>0 hrs</span>
                    <span>8+ hrs</span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {improvementData?.recommendations.sleep.description ||
                      smashData.social_history.sleep.description}
                  </p>
                </div>

                {/* Alcohol Consumption */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className="block text-sm font-medium">
                      Alcohol Consumption
                    </label>
                    {improvementData &&
                      improvementData.recommendations.alcohol.rating !==
                        alcoholIntake && (
                        <span
                          className={`text-xs font-medium ${
                            improvementData.recommendations.alcohol.rating <
                            alcoholIntake
                              ? "text-green-600"
                              : "text-red-600"
                          }`}
                        >
                          {improvementData.recommendations.alcohol.rating <
                          alcoholIntake
                            ? "-"
                            : "+"}
                          {Math.abs(
                            improvementData.recommendations.alcohol.rating -
                              alcoholIntake
                          )}
                        </span>
                      )}
                  </div>
                  <div className="relative">
                    {improvementData ? (
                      <>
                        {/* Improvement bar (black) */}
                        <Progress
                          value={
                            improvementData.recommendations.alcohol.rating * 10
                          }
                          className="w-full"
                        />
                        {/* Difference overlay (green for reduction, red for increase) */}
                        {improvementData.recommendations.alcohol.rating !==
                          alcoholIntake && (
                          <div
                            className={`absolute transition-all duration-700 ease-out ${
                              improvementData.recommendations.alcohol.rating <
                              alcoholIntake
                                ? "bg-green-500"
                                : "bg-red-500"
                            }`}
                            style={{
                              left:
                                improvementData.recommendations.alcohol.rating <
                                alcoholIntake
                                  ? `${
                                      improvementData.recommendations.alcohol
                                        .rating * 10
                                    }%`
                                  : `${alcoholIntake * 10}%`,
                              width: `${
                                Math.abs(
                                  improvementData.recommendations.alcohol
                                    .rating - alcoholIntake
                                ) * 10
                              }%`,
                              height: "100%",
                              top: 0,
                            }}
                          />
                        )}
                      </>
                    ) : (
                      <Progress value={alcoholIntake * 10} className="w-full" />
                    )}
                  </div>
                  <div className="flex justify-between text-xs text-muted-foreground mt-1">
                    <span>0</span>
                    <span>14+ drinks</span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {improvementData?.recommendations.alcohol.description ||
                      smashData.social_history.alcohol.description}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* CTA Button */}
            <Button
              className="w-full"
              size="lg"
              onClick={handleVisitDoctor}
              disabled={isVisitLoading}
            >
              {isVisitLoading ? "Visiting..." : `Visit ${smashData.pcp.name}`}
            </Button>

            {/* Recommendations Card */}
            {improvementData && (
              <Card>
                <CardHeader>
                  <CardTitle>Your Personalized Recommendations</CardTitle>
                  <CardDescription>
                    Based on your visit with {smashData.pcp.name}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Exercise Recommendation */}
                  <div className="border-b pb-3 last:border-b-0">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <span className="font-medium text-sm">Exercise</span>
                    </div>
                    <p className="text-sm text-muted-foreground pl-4">
                      {improvementData.recommendations.exercise.description}
                    </p>
                    {improvementData.evidence_urls?.exercise && (
                      <div className="pl-4 mt-2">
                        <p className="text-xs font-medium text-muted-foreground mb-1">
                          Evidence:
                        </p>
                        <div className="space-y-1">
                          {improvementData.evidence_urls.exercise.map(
                            (url, index) => (
                              <a
                                key={index}
                                href={url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 hover:underline"
                              >
                                <ExternalLink className="h-3 w-3" />
                                {url.replace(/https?:\/\//, "").split("/")[0]}
                              </a>
                            )
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Sleep Recommendation */}
                  <div className="border-b pb-3 last:border-b-0">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                      <span className="font-medium text-sm">Sleep</span>
                    </div>
                    <p className="text-sm text-muted-foreground pl-4">
                      {improvementData.recommendations.sleep.description}
                    </p>
                    {improvementData.evidence_urls?.sleep && (
                      <div className="pl-4 mt-2">
                        <p className="text-xs font-medium text-muted-foreground mb-1">
                          Evidence:
                        </p>
                        <div className="space-y-1">
                          {improvementData.evidence_urls.sleep.map(
                            (url, index) => (
                              <a
                                key={index}
                                href={url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 hover:underline"
                              >
                                <ExternalLink className="h-3 w-3" />
                                {url.replace(/https?:\/\//, "").split("/")[0]}
                              </a>
                            )
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Alcohol Recommendation */}
                  <div className="border-b pb-3 last:border-b-0">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-2 h-2 bg-amber-500 rounded-full"></div>
                      <span className="font-medium text-sm">Alcohol</span>
                    </div>
                    <p className="text-sm text-muted-foreground pl-4">
                      {improvementData.recommendations.alcohol.description}
                    </p>
                    {improvementData.evidence_urls?.alcohol && (
                      <div className="pl-4 mt-2">
                        <p className="text-xs font-medium text-muted-foreground mb-1">
                          Evidence:
                        </p>
                        <div className="space-y-1">
                          {improvementData.evidence_urls.alcohol.map(
                            (url, index) => (
                              <a
                                key={index}
                                href={url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 hover:underline"
                              >
                                <ExternalLink className="h-3 w-3" />
                                {url.replace(/https?:\/\//, "").split("/")[0]}
                              </a>
                            )
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Supplements Recommendations */}
                  {improvementData.recommendations.supplements &&
                    improvementData.recommendations.supplements.length > 0 && (
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                          <span className="font-medium text-sm">
                            Supplements
                          </span>
                        </div>
                        <div className="pl-4 space-y-2">
                          {improvementData.recommendations.supplements.map(
                            (supplement, index) => (
                              <p
                                key={index}
                                className="text-sm text-muted-foreground"
                              >
                                {supplement.description}
                              </p>
                            )
                          )}
                        </div>
                        {improvementData.evidence_urls?.supplements && (
                          <div className="pl-4 mt-2">
                            <p className="text-xs font-medium text-muted-foreground mb-1">
                              Evidence:
                            </p>
                            <div className="space-y-1">
                              {improvementData.evidence_urls.supplements.map(
                                (url, index) => (
                                  <a
                                    key={index}
                                    href={url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 hover:underline"
                                  >
                                    <ExternalLink className="h-3 w-3" />
                                    {
                                      url
                                        .replace(/https?:\/\//, "")
                                        .split("/")[0]
                                    }
                                  </a>
                                )
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                </CardContent>
              </Card>
            )}
          </div>

          {/* Middle Column - Health Cards */}
          <div className="space-y-4">
            {/* Life Expectancy */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Life Expectancy</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3">
                  <div className="text-2xl font-bold text-primary mb-1">
                    {smashData.forecast.life_expectancy_years} years
                  </div>
                  {improvementData &&
                    improvementData.forecast.life_expectancy_years !==
                      smashData.forecast.life_expectancy_years && (
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground">→</span>
                        <div className="text-2xl font-bold text-green-600">
                          {improvementData.forecast.life_expectancy_years} years
                        </div>
                        <span className="text-xs text-green-600 font-medium">
                          +
                          {(
                            improvementData.forecast.life_expectancy_years -
                            smashData.forecast.life_expectancy_years
                          ).toFixed(1)}{" "}
                          years
                        </span>
                      </div>
                    )}
                </div>
                <div className="text-sm text-muted-foreground">
                  CI: 78-87 years
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  Based on 15 studies
                </div>
              </CardContent>
            </Card>

            {/* Cardiovascular Risk */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">
                  10-Year Cardiovascular Risk
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3">
                  <div
                    className={`text-2xl font-bold ${
                      Math.round(
                        smashData.forecast
                          .cardiovascular_event_10yr_probability * 100
                      ) < 5
                        ? "text-green-600"
                        : Math.round(
                            smashData.forecast
                              .cardiovascular_event_10yr_probability * 100
                          ) <= 10
                        ? "text-yellow-600"
                        : "text-red-600"
                    }`}
                  >
                    {Math.round(
                      smashData.forecast.cardiovascular_event_10yr_probability *
                        100
                    )}
                    %
                  </div>
                  {improvementData &&
                    improvementData.forecast
                      .cardiovascular_event_10yr_probability !==
                      smashData.forecast
                        .cardiovascular_event_10yr_probability && (
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground">→</span>
                        <div
                          className={`text-2xl font-bold ${
                            Math.round(
                              improvementData.forecast
                                .cardiovascular_event_10yr_probability * 100
                            ) < 5
                              ? "text-green-600"
                              : Math.round(
                                  improvementData.forecast
                                    .cardiovascular_event_10yr_probability * 100
                                ) <= 10
                              ? "text-yellow-600"
                              : "text-red-600"
                          }`}
                        >
                          {Math.round(
                            improvementData.forecast
                              .cardiovascular_event_10yr_probability * 100
                          )}
                          %
                        </div>
                        <span className="text-xs text-green-600 font-medium">
                          {improvementData.forecast
                            .cardiovascular_event_10yr_probability <
                          smashData.forecast
                            .cardiovascular_event_10yr_probability
                            ? `-${Math.round(
                                (smashData.forecast
                                  .cardiovascular_event_10yr_probability -
                                  improvementData.forecast
                                    .cardiovascular_event_10yr_probability) *
                                  100
                              )}% improvement`
                            : `+${Math.round(
                                (improvementData.forecast
                                  .cardiovascular_event_10yr_probability -
                                  smashData.forecast
                                    .cardiovascular_event_10yr_probability) *
                                  100
                              )}% increase`}
                        </span>
                      </div>
                    )}
                </div>
              </CardContent>
            </Card>

            {/* Energy Levels */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Energy Levels</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2 flex-wrap">
                  {smashData.forecast.energy_level === "Low" && (
                    <Badge
                      variant="default"
                      className="text-lg px-4 py-2 bg-red-100 text-red-800 hover:bg-red-100"
                    >
                      Low
                    </Badge>
                  )}
                  {smashData.forecast.energy_level === "Medium" && (
                    <Badge
                      variant="default"
                      className="text-lg px-4 py-2 bg-yellow-100 text-yellow-800 hover:bg-yellow-100"
                    >
                      Medium
                    </Badge>
                  )}
                  {smashData.forecast.energy_level === "High" && (
                    <Badge
                      variant="default"
                      className="text-lg px-4 py-2 bg-green-100 text-green-800 hover:bg-green-100"
                    >
                      High
                    </Badge>
                  )}

                  {improvementData &&
                    improvementData.forecast.energy_level !==
                      smashData.forecast.energy_level && (
                      <>
                        <span className="text-sm text-muted-foreground">→</span>
                        <Badge
                          variant="default"
                          className={`text-lg px-4 py-2 ${
                            improvementData.forecast.energy_level === "High"
                              ? "bg-green-100 text-green-800 hover:bg-green-100"
                              : improvementData.forecast.energy_level ===
                                "Medium"
                              ? "bg-yellow-100 text-yellow-800 hover:bg-yellow-100"
                              : "bg-red-100 text-red-800 hover:bg-red-100"
                          }`}
                        >
                          {improvementData.forecast.energy_level}
                        </Badge>
                        <span className="text-xs text-green-600 font-medium">
                          Improved!
                        </span>
                      </>
                    )}
                </div>
              </CardContent>
            </Card>

            {/* Metabolic Disease Risk */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">
                  Metabolic Disease Risk
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2 flex-wrap">
                  {smashData.forecast.metabolic_disease_risk === "Low" && (
                    <Badge
                      variant="default"
                      className="text-lg px-4 py-2 bg-green-100 text-green-800 hover:bg-green-100"
                    >
                      Low
                    </Badge>
                  )}
                  {smashData.forecast.metabolic_disease_risk === "Medium" && (
                    <Badge
                      variant="default"
                      className="text-lg px-4 py-2 bg-yellow-100 text-yellow-800 hover:bg-yellow-100"
                    >
                      Medium
                    </Badge>
                  )}
                  {smashData.forecast.metabolic_disease_risk === "High" && (
                    <Badge
                      variant="default"
                      className="text-lg px-4 py-2 bg-red-100 text-red-800 hover:bg-red-100"
                    >
                      High
                    </Badge>
                  )}

                  {improvementData &&
                    improvementData.forecast.metabolic_disease_risk !==
                      smashData.forecast.metabolic_disease_risk && (
                      <>
                        <span className="text-sm text-muted-foreground">→</span>
                        <Badge
                          variant="default"
                          className={`text-lg px-4 py-2 ${
                            improvementData.forecast.metabolic_disease_risk ===
                            "Low"
                              ? "bg-green-100 text-green-800 hover:bg-green-100"
                              : improvementData.forecast
                                  .metabolic_disease_risk === "Medium"
                              ? "bg-yellow-100 text-yellow-800 hover:bg-yellow-100"
                              : "bg-red-100 text-red-800 hover:bg-red-100"
                          }`}
                        >
                          {improvementData.forecast.metabolic_disease_risk}
                        </Badge>
                        <span className="text-xs text-green-600 font-medium">
                          Improved!
                        </span>
                      </>
                    )}
                </div>
              </CardContent>
            </Card>

            {/* Cognitive Disease Risk */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">
                  Cognitive Disease Risk
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2 flex-wrap">
                  {smashData.forecast.dementia_risk === "Low" && (
                    <Badge
                      variant="default"
                      className="text-lg px-4 py-2 bg-green-100 text-green-800 hover:bg-green-100"
                    >
                      Low
                    </Badge>
                  )}
                  {smashData.forecast.dementia_risk === "Moderate" && (
                    <Badge
                      variant="default"
                      className="text-lg px-4 py-2 bg-yellow-100 text-yellow-800 hover:bg-yellow-100"
                    >
                      Medium
                    </Badge>
                  )}
                  {smashData.forecast.dementia_risk === "High" && (
                    <Badge
                      variant="default"
                      className="text-lg px-4 py-2 bg-red-100 text-red-800 hover:bg-red-100"
                    >
                      High
                    </Badge>
                  )}

                  {improvementData &&
                    improvementData.forecast.dementia_risk !==
                      smashData.forecast.dementia_risk && (
                      <>
                        <span className="text-sm text-muted-foreground">→</span>
                        <Badge
                          variant="default"
                          className={`text-lg px-4 py-2 ${
                            improvementData.forecast.dementia_risk === "Low"
                              ? "bg-green-100 text-green-800 hover:bg-green-100"
                              : improvementData.forecast.dementia_risk ===
                                "Moderate"
                              ? "bg-yellow-100 text-yellow-800 hover:bg-yellow-100"
                              : "bg-red-100 text-red-800 hover:bg-red-100"
                          }`}
                        >
                          {improvementData.forecast.dementia_risk === "Moderate"
                            ? "Medium"
                            : improvementData.forecast.dementia_risk}
                        </Badge>
                        <span className="text-xs text-green-600 font-medium">
                          Improved!
                        </span>
                      </>
                    )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Patient Info & Image Upload */}
          <div className="space-y-4">
            <ImageUpload smashData={improvementData || smashData} />
          </div>
        </div>
      </div>
    </div>
  );
}
