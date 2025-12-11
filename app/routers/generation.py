"""LDIF Generation API endpoints."""
import csv
import io
import json
import logging
from typing import Optional

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse

from app.models.generation_models import (
    GenerationJob,
    GenerationRequest,
    GenerationResponse,
)
from app.services.generation_service import GenerationService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/jobs", response_model=GenerationJob, tags=["generation"])
async def create_generation_job(request: GenerationRequest) -> GenerationJob:
    """
    Create a new LDIF generation job.

    Args:
        request: Generation request with data and schema

    Returns:
        Created job with job_id
    """
    if not request.data:
        raise HTTPException(status_code=400, detail="Data cannot be empty")

    logger.info(f"Creating generation job with {len(request.data)} records")
    job = GenerationService.create_job(request)
    return job


@router.post("/generate", response_model=GenerationResponse, tags=["generation"])
async def generate_ldif(request: GenerationRequest) -> GenerationResponse:
    """
    Generate LDIF output from data.

    Args:
        request: Generation request

    Returns:
        Generation response with LDIF output
    """
    if not request.data:
        raise HTTPException(status_code=400, detail="Data cannot be empty")

    logger.info(f"Generating LDIF for {len(request.data)} records")
    job = GenerationService.create_job(request)
    response = GenerationService.process_generation(job.job_id, request)

    if response.status.value == "failed":
        logger.error(f"Generation failed: {response.message}")
        raise HTTPException(status_code=400, detail=response.message)

    return response


@router.post("/upload/csv", response_model=GenerationJob, tags=["generation"])
async def upload_csv(
    file: UploadFile = File(...),
    schema_name: str = Form(default="user"),
    base_dn: str = Form(default=""),
) -> GenerationJob:
    """
    Upload a CSV file for LDIF generation.

    Args:
        file: CSV file to upload
        schema_name: Schema name for validation
        base_dn: Base DN for LDIF entries

    Returns:
        Creation job
    """
    try:
        content = await file.read()
        csv_content = content.decode("utf-8")

        logger.info(f"Uploaded CSV file: {file.filename}")

        reader = csv.DictReader(io.StringIO(csv_content))
        data = [row for row in reader]

        if not data:
            raise HTTPException(status_code=400, detail="CSV file is empty")

        request = GenerationRequest(
            data=data,
            schema_name=schema_name,
            base_dn=base_dn,
        )
        job = GenerationService.create_job(request)
        return job

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CSV upload failed: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"CSV upload failed: {str(e)}"
        )


@router.post("/upload/json", response_model=GenerationJob, tags=["generation"])
async def upload_json(
    file: UploadFile = File(...),
    schema_name: str = Form(default="user"),
    base_dn: str = Form(default=""),
) -> GenerationJob:
    """
    Upload a JSON file for LDIF generation.

    Args:
        file: JSON file to upload
        schema_name: Schema name for validation
        base_dn: Base DN for LDIF entries

    Returns:
        Creation job
    """
    try:
        content = await file.read()
        json_content = content.decode("utf-8")

        logger.info(f"Uploaded JSON file: {file.filename}")

        parsed = json.loads(json_content)

        # Handle various JSON structures
        if isinstance(parsed, list):
            data = parsed
        elif isinstance(parsed, dict):
            for key in ["data", "records", "items"]:
                if key in parsed and isinstance(parsed[key], list):
                    data = parsed[key]
                    break
            else:
                data = [parsed]
        else:
            raise ValueError("Invalid JSON structure")

        if not data:
            msg = "JSON file contains no records"
            raise HTTPException(status_code=400, detail=msg)

        request = GenerationRequest(
            data=data,
            schema_name=schema_name,
            base_dn=base_dn,
        )
        job = GenerationService.create_job(request)
        return job

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"JSON upload failed: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"JSON upload failed: {str(e)}"
        )


@router.get("/jobs/{job_id}", response_model=GenerationJob, tags=["generation"])
async def get_job_status(job_id: str) -> GenerationJob:
    """
    Get the status of a generation job.

    Args:
        job_id: Job ID

    Returns:
        Job status
    """
    job = GenerationService.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    logger.info(f"Retrieved job status: {job_id}")
    return job


@router.get("/jobs/{job_id}/result", tags=["generation"])
async def get_job_result(job_id: str, download: bool = False):
    """
    Get the result of a completed generation job.

    Args:
        job_id: Job ID
        download: If True, return as downloadable file

    Returns:
        LDIF output or streaming response
    """
    job = GenerationService.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status.value != "completed":
        msg = f"Job is {job.status.value}, cannot retrieve result"
        raise HTTPException(status_code=400, detail=msg)

    result = GenerationService.get_job_result(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    logger.info(f"Retrieved result for job {job_id}")

    if download:
        return StreamingResponse(
            iter([result]),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename=ldif_{job_id}.ldif"
            },
        )

    return {"job_id": job_id, "output": result}


@router.post(
    "/jobs/{job_id}/process",
    response_model=GenerationResponse,
    tags=["generation"],
)
async def process_job(job_id: str) -> GenerationResponse:
    """
    Process a pending generation job.

    Args:
        job_id: Job ID

    Returns:
        Generation response
    """
    job = GenerationService.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status.value != "pending":
        msg = f"Job is {job.status.value}, cannot process"
        raise HTTPException(status_code=400, detail=msg)

    logger.info(f"Processing job {job_id}")

    # Reconstruct request from job data
    request = GenerationRequest(data=[], schema_name="user", base_dn="")

    response = GenerationService.process_generation(job_id, request)
    return response


@router.get("/schemas", tags=["generation"])
async def list_schemas():
    """List available schemas for generation."""
    logger.info("Listed available schemas")
    return {
        "schemas": list(GenerationService.AVAILABLE_SCHEMAS.keys()),
        "details": GenerationService.AVAILABLE_SCHEMAS,
    }


@router.get("/jobs", tags=["generation"])
async def list_jobs(status: Optional[str] = None):
    """
    List all generation jobs, optionally filtered by status.

    Args:
        status: Optional status filter

    Returns:
        List of jobs
    """
    from app.services.generation_service import _jobs

    jobs = list(_jobs.values())

    if status:
        jobs = [j for j in jobs if j.status.value == status]

    logger.info(f"Listed {len(jobs)} jobs")
    return {"jobs": jobs}
