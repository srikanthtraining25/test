"""LDIF generation service."""
import uuid
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.models.generation_models import (
    JobStatus,
    GenerationJob,
    GenerationRequest,
    GenerationResponse,
)
from app.schemas.data_schemas import USER_SCHEMA, PRODUCT_SCHEMA, TRANSACTION_SCHEMA
from app.services.ldif.models import User, LDAPEntry
from app.services.ldif.generator import LDIFGenerator

logger = logging.getLogger(__name__)

# In-memory job storage (in production, use a database)
_jobs: Dict[str, GenerationJob] = {}
_job_results: Dict[str, str] = {}


class GenerationService:
    """Service for managing LDIF generation jobs."""

    # Available schemas
    AVAILABLE_SCHEMAS = {
        "user": USER_SCHEMA.model_dump(),
        "product": PRODUCT_SCHEMA.model_dump(),
        "transaction": TRANSACTION_SCHEMA.model_dump(),
    }

    @staticmethod
    def create_job(request: GenerationRequest) -> GenerationJob:
        """
        Create a new generation job.
        
        Args:
            request: Generation request
            
        Returns:
            Created job
        """
        job_id = str(uuid.uuid4())
        job = GenerationJob(
            job_id=job_id,
            status=JobStatus.PENDING,
            created_at=datetime.now(),
            input_records=len(request.data),
        )
        _jobs[job_id] = job
        logger.info(f"Created generation job {job_id} with {len(request.data)} records")
        return job

    @staticmethod
    def get_job(job_id: str) -> Optional[GenerationJob]:
        """
        Get a job by ID.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job or None if not found
        """
        return _jobs.get(job_id)

    @staticmethod
    def get_job_result(job_id: str) -> Optional[str]:
        """
        Get the result of a completed job.
        
        Args:
            job_id: Job ID
            
        Returns:
            LDIF output or None if not found/not completed
        """
        job = _jobs.get(job_id)
        if job and job.status == JobStatus.COMPLETED:
            return _job_results.get(job_id)
        return None

    @staticmethod
    def process_generation(
        job_id: str, request: GenerationRequest
    ) -> GenerationResponse:
        """
        Process a generation request.
        
        Args:
            job_id: Job ID
            request: Generation request
            
        Returns:
            Generation response
        """
        job = _jobs.get(job_id)
        if not job:
            return GenerationResponse(
                job_id=job_id,
                status=JobStatus.FAILED,
                message="Job not found",
                error_details={"error": "Job not found"},
            )

        try:
            job.status = JobStatus.PROCESSING
            job.started_at = datetime.now()
            logger.info(f"Processing job {job_id}")

            # Validate schema exists
            if request.schema_name not in GenerationService.AVAILABLE_SCHEMAS:
                error_msg = f"Schema '{request.schema_name}' not found"
                job.status = JobStatus.FAILED
                job.error_message = error_msg
                logger.error(f"Job {job_id}: {error_msg}")
                return GenerationResponse(
                    job_id=job_id,
                    status=JobStatus.FAILED,
                    message=error_msg,
                    error_details={"error": error_msg},
                )

            # Convert data to LDAP entries
            entries: List[LDAPEntry] = []
            for i, record in enumerate(request.data):
                try:
                    entry = GenerationService._record_to_ldap_entry(
                        record, request
                    )
                    if entry:
                        entries.append(entry)
                except Exception as e:
                    logger.warning(f"Failed to convert record {i}: {str(e)}")

            if not entries:
                error_msg = "No valid LDAP entries generated"
                job.status = JobStatus.FAILED
                job.error_message = error_msg
                logger.error(f"Job {job_id}: {error_msg}")
                return GenerationResponse(
                    job_id=job_id,
                    status=JobStatus.FAILED,
                    message=error_msg,
                    error_details={"error": error_msg},
                )

            # Generate LDIF
            if request.format == "json":
                output = json.dumps(
                    [
                        {
                            "dn": entry.dn,
                            "objectClass": entry.object_classes,
                            "attributes": entry.attributes,
                        }
                        for entry in entries
                    ],
                    indent=2,
                )
            else:
                output = LDIFGenerator.generate(entries)

            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            job.output_records = len(entries)
            job.progress_percentage = 100
            _job_results[job_id] = output
            logger.info(f"Job {job_id} completed with {len(entries)} entries")

            return GenerationResponse(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                message="Generation completed successfully",
                output=output,
                record_count=len(entries),
            )

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            logger.error(f"Job {job_id} failed: {str(e)}")
            return GenerationResponse(
                job_id=job_id,
                status=JobStatus.FAILED,
                message=f"Generation failed: {str(e)}",
                error_details={"error": str(e)},
            )

    @staticmethod
    def _record_to_ldap_entry(
        record: Dict[str, Any], request: GenerationRequest
    ) -> Optional[LDAPEntry]:
        """
        Convert a data record to an LDAP entry.
        
        Args:
            record: Data record
            request: Generation request
            
        Returns:
            LDAP entry or None
        """
        base_dn = request.base_dn or "dc=example,dc=com"
        schema_name = request.schema_name

        if schema_name == "user":
            uid = record.get("id") or record.get("uid")
            cn = record.get("name") or record.get("cn")
            sn = record.get("name", "").split()[-1] if record.get("name") else "User"

            if uid and cn:
                attributes = {}
                if "email" in record and record["email"]:
                    attributes["mail"] = [record["email"]]
                if "age" in record:
                    attributes["age"] = [str(record["age"])]

                return User(
                    uid=str(uid),
                    parent_dn=base_dn,
                    cn=str(cn),
                    sn=str(sn),
                    additional_attributes=attributes if attributes else None,
                )

        return None
