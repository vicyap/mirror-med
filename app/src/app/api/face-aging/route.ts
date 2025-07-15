import { NextRequest, NextResponse } from "next/server";
import OpenAI from "openai";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || "placeholder-key",
});

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const image = formData.get("image") as File;
    const smashData = formData.get("smash") as string;

    if (!image || !smashData) {
      return NextResponse.json(
        { error: "Both image and smash data are required" },
        { status: 400 }
      );
    }

    if (!process.env.OPENAI_API_KEY) {
      return NextResponse.json(
        { error: "OpenAI API key not configured" },
        { status: 500 }
      );
    }

    let parsedSmashData;
    try {
      parsedSmashData = JSON.parse(smashData);
    } catch {
      return NextResponse.json(
        { error: "Invalid JSON in smash data" },
        { status: 400 }
      );
    }

    const response = await openai.images.edit({
      model: "gpt-image-1",
      image: image,
      prompt: `
              Using the provided smash model can you generate a new image of the face to show what it's going to look like in 5 years? 

Health and lifestyle data: ${JSON.stringify(parsedSmashData, null, 2)}

This person is currently 30 years old.

Please analyze the health data and describe how this person's face might age over the next 10 years based on their lifestyle, medical history, and risk factors.`,

      n: 1,
      size: "1024x1024",
      quality: "medium",
      // response_format: "b64_json",
    });

    // console.log(response.data);

    // Convert b64_json to data URL
    const base64Data = response.data?.[0]?.b64_json;
    const imageDataUrl = base64Data
      ? `data:image/png;base64,${base64Data}`
      : null;

    return NextResponse.json({
      prediction: imageDataUrl,
      model_used: "dall-e-2",
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("OpenAI API error:", error);
    return NextResponse.json(
      { error: "Failed to process face aging prediction" },
      { status: 500 }
    );
  }
}
