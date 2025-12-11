"""Integration tests for LDIF generation API."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestGenerationEndpoints:
    """Test LDIF generation endpoints."""

    def test_list_schemas(self):
        """Test listing available schemas."""
        response = client.get("/api/v1/generation/schemas")
        assert response.status_code == 200
        
        data = response.json()
        assert "schemas" in data
        assert "user" in data["schemas"]
        assert "product" in data["schemas"]
        assert "transaction" in data["schemas"]

    def test_create_job(self):
        """Test creating a generation job."""
        payload = {
            "data": [
                {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 25}
            ],
            "schema_name": "user",
            "base_dn": "dc=example,dc=com",
        }
        response = client.post("/api/v1/generation/jobs", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"
        assert data["input_records"] == 1

    def test_create_job_empty_data(self):
        """Test creating a job with empty data."""
        payload = {
            "data": [],
            "schema_name": "user",
        }
        response = client.post("/api/v1/generation/jobs", json=payload)
        assert response.status_code == 400

    def test_generate_ldif(self):
        """Test generating LDIF directly."""
        payload = {
            "data": [
                {
                    "id": 1,
                    "name": "Jane Smith",
                    "email": "jane@example.com",
                    "age": 30,
                }
            ],
            "schema_name": "user",
            "base_dn": "dc=example,dc=com",
            "format": "ldif",
        }
        response = client.post("/api/v1/generation/generate", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "completed"
        assert "output" in data
        assert data["record_count"] == 1
        assert "dn:" in data["output"]
        assert "objectClass: inetOrgPerson" in data["output"]

    def test_generate_ldif_json_format(self):
        """Test generating LDIF in JSON format."""
        payload = {
            "data": [
                {
                    "id": 1,
                    "name": "Test User",
                    "email": "test@example.com",
                }
            ],
            "schema_name": "user",
            "format": "json",
        }
        response = client.post("/api/v1/generation/generate", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "completed"
        assert "output" in data
        
        # Verify it's valid JSON
        import json
        output = json.loads(data["output"])
        assert isinstance(output, list)
        assert len(output) == 1
        assert "dn" in output[0]
        assert "objectClass" in output[0]

    def test_get_job_status(self):
        """Test getting job status."""
        # Create a job first
        payload = {
            "data": [{"id": 1, "name": "Test", "email": "test@example.com"}],
            "schema_name": "user",
        }
        create_response = client.post("/api/v1/generation/jobs", json=payload)
        job_id = create_response.json()["job_id"]
        
        # Get status
        response = client.get(f"/api/v1/generation/jobs/{job_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["job_id"] == job_id
        assert data["status"] in ["pending", "processing", "completed", "failed"]

    def test_get_nonexistent_job(self):
        """Test getting a non-existent job."""
        response = client.get("/api/v1/generation/jobs/nonexistent-id")
        assert response.status_code == 404

    def test_list_jobs(self):
        """Test listing jobs."""
        response = client.get("/api/v1/generation/jobs")
        assert response.status_code == 200
        
        data = response.json()
        assert "jobs" in data
        assert isinstance(data["jobs"], list)

    def test_list_jobs_filter_by_status(self):
        """Test listing jobs with status filter."""
        response = client.get("/api/v1/generation/jobs?status=pending")
        assert response.status_code == 200
        
        data = response.json()
        assert "jobs" in data

    def test_get_job_result_before_completion(self):
        """Test getting result of incomplete job."""
        # Create a job
        payload = {
            "data": [{"id": 1, "name": "Test", "email": "test@example.com"}],
            "schema_name": "user",
        }
        create_response = client.post("/api/v1/generation/jobs", json=payload)
        job_id = create_response.json()["job_id"]
        
        # Try to get result before processing
        response = client.get(f"/api/v1/generation/jobs/{job_id}/result")
        assert response.status_code == 400

    def test_generate_multiple_records(self):
        """Test generating LDIF from multiple records."""
        payload = {
            "data": [
                {"id": 1, "name": "User One", "email": "user1@example.com", "age": 25},
                {"id": 2, "name": "User Two", "email": "user2@example.com", "age": 30},
                {"id": 3, "name": "User Three", "email": "user3@example.com", "age": 35},
            ],
            "schema_name": "user",
            "base_dn": "ou=users,dc=example,dc=com",
        }
        response = client.post("/api/v1/generation/generate", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "completed"
        assert data["record_count"] == 3

    def test_generate_with_invalid_schema(self):
        """Test generating with invalid schema."""
        payload = {
            "data": [{"id": 1, "name": "Test"}],
            "schema_name": "invalid_schema",
        }
        response = client.post("/api/v1/generation/generate", json=payload)
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    def test_api_health(self):
        """Test API health check."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"

    def test_api_readiness(self):
        """Test API readiness check."""
        response = client.get("/api/v1/ready")
        assert response.status_code == 200


class TestCSVUpload:
    """Test CSV upload functionality."""

    def test_upload_csv(self):
        """Test uploading a CSV file."""
        csv_content = b"id,name,email,age\n1,John Doe,john@example.com,25\n2,Jane Smith,jane@example.com,30"
        
        response = client.post(
            "/api/v1/generation/upload/csv",
            files={"file": ("test.csv", csv_content)},
            data={"schema_name": "user", "base_dn": "dc=example,dc=com"},
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"
        assert data["input_records"] == 2

    def test_upload_empty_csv(self):
        """Test uploading empty CSV."""
        csv_content = b""
        
        response = client.post(
            "/api/v1/generation/upload/csv",
            files={"file": ("test.csv", csv_content)},
            data={"schema_name": "user"},
        )
        assert response.status_code == 400

    def test_upload_csv_no_file(self):
        """Test uploading without file."""
        response = client.post(
            "/api/v1/generation/upload/csv",
            data={"schema_name": "user"},
        )
        assert response.status_code == 422


class TestJSONUpload:
    """Test JSON upload functionality."""

    def test_upload_json_array(self):
        """Test uploading a JSON array file."""
        json_content = b'[{"id": 1, "name": "John", "email": "john@example.com"}, {"id": 2, "name": "Jane", "email": "jane@example.com"}]'
        
        response = client.post(
            "/api/v1/generation/upload/json",
            files={"file": ("test.json", json_content)},
            data={"schema_name": "user"},
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "job_id" in data
        assert data["input_records"] == 2

    def test_upload_json_object_with_data(self):
        """Test uploading JSON with data field."""
        json_content = b'{"data": [{"id": 1, "name": "John", "email": "john@example.com"}]}'
        
        response = client.post(
            "/api/v1/generation/upload/json",
            files={"file": ("test.json", json_content)},
            data={"schema_name": "user"},
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["input_records"] == 1

    def test_upload_json_object_with_records(self):
        """Test uploading JSON with records field."""
        json_content = b'{"records": [{"id": 1, "name": "John", "email": "john@example.com"}]}'
        
        response = client.post(
            "/api/v1/generation/upload/json",
            files={"file": ("test.json", json_content)},
            data={"schema_name": "user"},
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["input_records"] == 1

    def test_upload_empty_json(self):
        """Test uploading empty JSON array."""
        json_content = b'[]'
        
        response = client.post(
            "/api/v1/generation/upload/json",
            files={"file": ("test.json", json_content)},
            data={"schema_name": "user"},
        )
        assert response.status_code == 400

    def test_upload_invalid_json(self):
        """Test uploading invalid JSON."""
        json_content = b'{invalid json}'
        
        response = client.post(
            "/api/v1/generation/upload/json",
            files={"file": ("test.json", json_content)},
            data={"schema_name": "user"},
        )
        assert response.status_code == 400


class TestLDIFOutput:
    """Test LDIF output functionality."""

    def test_ldif_contains_dn(self):
        """Test that LDIF output contains DN."""
        payload = {
            "data": [
                {"id": 1, "name": "Test User", "email": "test@example.com"}
            ],
            "schema_name": "user",
            "base_dn": "dc=example,dc=com",
        }
        response = client.post("/api/v1/generation/generate", json=payload)
        
        data = response.json()
        output = data["output"]
        
        assert "dn: uid=1" in output
        assert "dc=example,dc=com" in output

    def test_ldif_contains_object_classes(self):
        """Test that LDIF output contains objectClass."""
        payload = {
            "data": [
                {"id": 1, "name": "Test User", "email": "test@example.com"}
            ],
            "schema_name": "user",
        }
        response = client.post("/api/v1/generation/generate", json=payload)
        
        data = response.json()
        output = data["output"]
        
        assert "objectClass: inetOrgPerson" in output
        assert "objectClass: person" in output

    def test_ldif_contains_attributes(self):
        """Test that LDIF output contains attributes."""
        payload = {
            "data": [
                {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "age": 25,
                }
            ],
            "schema_name": "user",
        }
        response = client.post("/api/v1/generation/generate", json=payload)
        
        data = response.json()
        output = data["output"]
        
        assert "cn: John Doe" in output
        assert "mail: john@example.com" in output

    def test_ldif_separates_entries(self):
        """Test that multiple LDIF entries are properly separated."""
        payload = {
            "data": [
                {"id": 1, "name": "User One", "email": "user1@example.com"},
                {"id": 2, "name": "User Two", "email": "user2@example.com"},
            ],
            "schema_name": "user",
        }
        response = client.post("/api/v1/generation/generate", json=payload)
        
        data = response.json()
        output = data["output"]
        
        # Should have empty line between entries
        assert "\n\ndn:" in output
