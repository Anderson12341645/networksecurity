import sys
import os
import logging  # Added logging

import certifi
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()
mongo_db_url = os.getenv("MONGODB_URL_KEY")
print(mongo_db_url)
import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Request, HTTPException  # Added HTTPException
from uvicorn import run as app_run
from fastapi.responses import Response, JSONResponse  # Added JSONResponse
from starlette.responses import RedirectResponse
import pandas as pd
import numpy as np  # Added numpy

from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create MongoDB client with timeout
try:
    logger.info("Connecting to MongoDB...")
    client = pymongo.MongoClient(
        mongo_db_url, 
        tlsCAFile=ca,
        serverSelectionTimeoutMS=5000  # 5-second timeout
    )
    # Verify connection
    client.server_info()
    logger.info("MongoDB connection successful")
except Exception as e:
    logger.error(f"MongoDB connection failed: {str(e)}")
    client = None  # Set client to None for graceful failure

from networksecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from networksecurity.constant.training_pipeline import DATA_INGESTION_DATABASE_NAME

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="./templates")

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return JSONResponse(content={"status": "ok"}, status_code=200)

@app.get("/train")
async def train_route():
    try:
        logger.info("Starting training pipeline...")
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        logger.info("Training completed successfully")
        return Response("Training is successful")
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/predict")
async def predict_route(request: Request, file: UploadFile = File(...)):
    try:
        logger.info("Starting prediction...")
        # Read and validate file
        if not file.filename.endswith('.csv'):
            raise ValueError("Only CSV files are supported")
            
        df = pd.read_csv(file.file)
        
        # Fix column name typos
        df.rename(columns={
            'Domain_registeration_length': 'Domain_registration_length',
            'popUpWidnow': 'popUpWindow'
        }, inplace=True)
        
        # Load model with error handling
        try:
            preprocesor = load_object("final_model/preprocessor.pkl")
            final_model = load_object("final_model/model.pkl")
        except Exception as e:
            logger.error(f"Model loading failed: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail="Model not found. Train model first."
            )
            
        network_model = NetworkModel(preprocessor=preprocesor, model=final_model)
        
        # Convert to numpy array for prediction
        y_pred = network_model.predict(df.values)
        df['predicted_column'] = y_pred
        
        # Save prediction
        os.makedirs('prediction_output', exist_ok=True)
        df.to_csv('prediction_output/output.csv')
        
        # Return simplified response instead of HTML
        return JSONResponse(content={
            "status": "success",
            "prediction_count": len(y_pred),
            "positive_predictions": int(np.sum(y_pred))
        })
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    
if __name__=="__main__":
    logger.info("Starting server on 0.0.0.0:8000...")
    app_run(app, host="0.0.0.0", port=8000, log_level="info")