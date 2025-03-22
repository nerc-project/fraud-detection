# Import the dependencies we need to run the code.
import os
import requests
import json
import gradio as gr
import numpy as np

# Get a few environment variables. These are so we:
# - Know what endpoint we should request
# - Set server name and port for Gradio
MODEL_NAME = os.getenv("MODEL_NAME", "fraud")               # You need to manually set this with an environment variable
REST_URL = os.getenv("INFERENCE_ENDPOINT")                  # You need to manually set this with an environment variable
INFER_URL = f"{REST_URL}/v2/models/{MODEL_NAME}/infer"

GRADIO_SERVER_PORT = int(os.getenv("GRADIO_SERVER_PORT"))   # Automatically set by the Dockerfile
GRADIO_SERVER_NAME = os.getenv("GRADIO_SERVER_NAME")        # Automatically set by the Dockerfile

# Create a small function that sends data to the inference endpoint and recieves a prediction
def predict(distance_from_last_transaction,ratio_to_median_purchase_price,used_chip,used_pin_number,online_order):
    payload = {
        "inputs": [
            {
                "name": "dense_input",
                "shape": [1, 5],
                "datatype": "FP32",
                "data": [distance_from_last_transaction,ratio_to_median_purchase_price,used_chip,used_pin_number,online_order]
            },
            ]
        }
    headers = {
        'content-type': 'application/json'
    }

    response = requests.post(INFER_URL, json=payload, headers=headers)
    prediction = response.json()['outputs'][0]['data'][0]
    print(prediction)
    return "Fraud" if prediction >=0.995 else "Not fraud"


# Create and launch a Gradio interface that uses the prediction function to predict an output based on the inputs.
# We also set up a few example inputs to make it easier to try out the application.
demo = gr.Interface(
    fn=predict,
    inputs=["number","number","number","number","number"],
    outputs="textbox",
    examples=[
        [0.0, 1.0, 1.0, 1.0, 0.0],
        [100.0, 1.2, 0.0, 0.0, 1.0]
        ],
    title="Credit Card Fraud Detection Application"
    )

demo.launch(server_name=GRADIO_SERVER_NAME, server_port=GRADIO_SERVER_PORT)
