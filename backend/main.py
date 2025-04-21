from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
import base64
from langgraph.graph import StateGraph, END
from typing import TypedDict
from openai import OpenAI
from twilio.rest import Client
import os
from dotenv import load_dotenv
from mistralai import Mistral
import json

load_dotenv()

# Agent state
class PlantState(TypedDict):
    image: bytes
    llm_response: str
    condition_detected: bool

# LLM Inference node
def llm_inference(state: PlantState):
    image_bytes = state['image']

    # Convert image bytes to a base64-encoded string
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    # Initialize the Pixtral client
    pixtral_client = Mistral(api_key=os.getenv("PIXTRAL_API_KEY"))  # Load API key from .env

    # Prepare the prompt and messages
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": 'Analyze this plant image in detail and provide:\n'
                            '1. Overall plant health status\n'
                            '2. Any signs of fungal diseases\n'
                            '3. Specific disease identification (if any)\n'
                            '4. Recommended actions\n'
                            'Format the response as a JSON object with these keys:\n'
                            'health_status, fungal_status, diseases_detected, recommendations'
                },
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{image_base64}"
                }
            ]
        }
    ]

    try:
        # Send the request to the Pixtral API
        response = pixtral_client.chat.complete(
            model="pixtral-12b-2409",
            messages=messages
        )

        # Extract the result from the response
        result_text = response.choices[0].message.content.strip().lower()

        # Check for disease-related keywords
        condition_detected = any(keyword in result_text for keyword in ["disease", "unhealthy", "infection", "fungus", "mildew"])

        return {
            "image": image_bytes,
            "llm_response": result_text,
            "condition_detected": condition_detected
        }
    except Exception as e:
        # Handle errors gracefully
        return {
            "image": image_bytes,
            "llm_response": f"Error: {str(e)}",
            "condition_detected": False
        }

# SMS Notification node
def notify_user(state: PlantState):
    if state["condition_detected"]:  # Only process if a condition is detected
        try:
            # Log the raw response for debugging
            print(f"Raw LLM Response: {state['llm_response']}")

            # Clean the response by removing backticks and extra formatting
            cleaned_response = state["llm_response"].strip("```").strip()

            # Remove the "json" prefix if it exists
            if cleaned_response.startswith("json"):
                cleaned_response = cleaned_response[len("json"):].strip()
            print(f"Cleaned LLM Response: {cleaned_response}")  # Debugging log

            # Attempt to parse the cleaned JSON response
            try:
                # Validate and clean the JSON
                response_data = json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                print(f"JSONDecodeError: {str(e)}")  # Log the specific error
                print("Invalid JSON response received after cleaning.")
                response_data = {
                    "health_status": "Unknown",
                    "fungal_status": "Unknown",
                    "diseases_detected": "None",
                    "recommendations": []
                }

            # Format the SMS message
            message_body = (
                f"🚨 Plant Issue Detected:\n"
                f"Health Status: {response_data.get('health_status', 'Unknown')}\n"
                f"Fungal Status: {response_data.get('fungal_status', 'Unknown')}\n"
                f"Diseases Detected: {response_data.get('diseases_detected', 'None')}\n"
                f"Recommendations: {', '.join(response_data.get('recommendations', []))}"
            )

            # Send the SMS
            client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN"))
            message = client.messages.create(
                body=message_body,
                from_=os.getenv("TWILIO_NUMBER"),
                to=os.getenv("USER_MOBILE_NUMBER")
            )
            print(f"Notification sent: {message.sid}")

            # Update the state with the formatted message
            state["notification_message"] = message_body

        except Exception as e:
            print(f"Failed to send SMS notification: {str(e)}")
            state["notification_message"] = "Failed to send SMS notification."
    else:
        print("Plant is healthy. No SMS sent.")
        state["notification_message"] = "Plant is healthy. No SMS sent."

    # Return the updated state
    return state

# LangGraph agent workflow
graph = StateGraph(PlantState)
graph.add_node("llm_inference", llm_inference)
graph.add_node("notify_user", notify_user)

graph.set_entry_point("llm_inference")
graph.add_conditional_edges(
    "llm_inference",
    lambda state: "notify_user" if state["condition_detected"] else END
)
graph.add_edge("notify_user", END)

plant_agent = graph.compile()

# FastAPI Setup
app = FastAPI()

@app.post("/check-health")
async def check_health(file: UploadFile = File(...)):
    image_bytes = await file.read()

    final_state = plant_agent.invoke({"image": image_bytes})

    msg = (
        f"⚠️ Disease detected: {final_state['llm_response']}"
        if final_state["condition_detected"]
        else f"✅ Plant is healthy: {final_state['llm_response']}"
    )

    return JSONResponse(content={"message": msg})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

