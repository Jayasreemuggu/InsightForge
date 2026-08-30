from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from pathlib import Path
import logging

import numpy as np
import pandas as pd

from backend.analysis_pipeline import run_analysis

from backend.feedback import (
    record_feedback,
    get_feedback_summary
)

from backend.security import validate_data_file

app = FastAPI(title="InsightForge API")
# ============================================================
# REQUEST VALIDATION
# ============================================================

class AnalyzeRequest(BaseModel):

    sales_file: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    feedback_file: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    region: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    date: str = Field(
        ...,
        min_length=8,
        max_length=20
    )

    persona: Literal[
        "Executive",
        "Manager",
        "Analyst"
    ] = "Executive"


class FeedbackRequest(BaseModel):

    region: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    date: str = Field(
        ...,
        min_length=8,
        max_length=20
    )

    kpi: str = Field(
        default="revenue",
        min_length=1,
        max_length=100
    )

    persona: Literal[
        "Executive",
        "Manager",
        "Analyst"
    ] = "Executive"

    feedback_type: str = Field(
        ...,
        min_length=1,
        max_length=50
    )

    rating: int | None = Field(
        default=None,
        ge=1,
        le=5
    )

    correction: str = Field(
        default="",
        max_length=2000
    )

    comment: str = Field(
        default="",
        max_length=2000
    )

@app.get("/")
def home():
    return {"message": "InsightForge API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


def make_json_safe(obj):
    """
    Recursively convert NumPy/pandas objects
    into standard Python JSON-compatible objects.
    """

    if isinstance(obj, dict):
        return {
            str(key): make_json_safe(value)
            for key, value in obj.items()
        }

    if isinstance(obj, list):
        return [
            make_json_safe(value)
            for value in obj
        ]

    if isinstance(obj, tuple):
        return [
            make_json_safe(value)
            for value in obj
        ]

    if isinstance(obj, pd.DataFrame):
        return make_json_safe(
            obj.to_dict(orient="records")
        )

    if isinstance(obj, pd.Series):
        return make_json_safe(
            obj.tolist()
        )

    if isinstance(obj, np.integer):
        return int(obj)

    if isinstance(obj, np.floating):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)

    if isinstance(obj, np.bool_):
        return bool(obj)

    if pd.isna(obj):
        return None

    return obj


@app.post("/analyze")
def analyze(request: AnalyzeRequest):

    try:

        # ----------------------------------------------------
        # Validate controlled data files
        # ----------------------------------------------------

        sales_file = validate_data_file(
            request.sales_file
        )

        feedback_file = validate_data_file(
            request.feedback_file
        )

        # ----------------------------------------------------
        # Validate date
        # ----------------------------------------------------

        try:
            pd.to_datetime(request.date)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format."
            )

        # ----------------------------------------------------
        # Run analysis
        # ----------------------------------------------------

        result = run_analysis(
            sales_file=sales_file,
            feedback_file=feedback_file,
            region=request.region,
            date=request.date,
            persona=request.persona
        )

        return make_json_safe(result)

    except HTTPException:
        raise

    except PermissionError as e:

        logging.warning(
            "Security violation during analysis: %s",
            str(e)
        )

        raise HTTPException(
            status_code=403,
            detail="Access denied."
        )

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail="Requested data file was not found."
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception:

        # Do NOT expose traceback to the client.
        logging.exception(
            "Unexpected error during KPI analysis."
        )

        raise HTTPException(
            status_code=500,
            detail="Internal analysis error."
        )

@app.post("/feedback")
def submit_feedback(request: FeedbackRequest):

    try:

        pd.to_datetime(request.date)

        result = record_feedback(
            region=request.region,
            date=request.date,
            kpi=request.kpi,
            persona=request.persona,
            feedback_type=request.feedback_type,
            rating=request.rating,
            correction=request.correction,
            comment=request.comment
        )

        return make_json_safe(result)

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception:

        logging.exception(
            "Unexpected error while recording feedback."
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to record feedback."
        )

@app.get("/feedback/summary")
def feedback_summary():

    return make_json_safe(
        get_feedback_summary()
    )