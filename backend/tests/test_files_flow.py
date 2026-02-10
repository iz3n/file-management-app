"""
Integration and end-to-end tests for the files API.
"""
import pytest


def test_upload_returns_200_and_shape(client):
    """Upload a valid CSV and assert response shape and status."""
    response = client.post(
        "/files/upload",
        files={"file": ("test.csv", b"a,b\n1,2")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "filename" in data
    assert data["rows"] == 1
    assert data["cols"] == 2
    assert data["size"] == 7


def test_upload_rejects_non_csv(client):
    """Upload with non-CSV extension returns 400."""
    response = client.post(
        "/files/upload",
        files={"file": ("data.txt", b"a,b\n1,2")},
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]


def test_list_files_increases_after_upload(client):
    """List files, upload one, then assert total increased by 1 and new file is listed."""
    list_resp = client.get("/files/", params={"page": 1, "page_size": 10})
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    initial_total = list_data["total"]

    upload_resp = client.post("/files/upload", files={"file": ("x.csv", b"a,b\n1,2")})
    assert upload_resp.status_code == 200
    uploaded_filename = upload_resp.json()["filename"]

    list_resp2 = client.get("/files/", params={"page": 1, "page_size": 10})
    assert list_resp2.status_code == 200
    list_data2 = list_resp2.json()
    assert list_data2["total"] == initial_total + 1
    assert len(list_data2["data"]) >= 1
    assert any(f["filename"] == uploaded_filename for f in list_data2["data"])


def test_get_metadata_404(client):
    """Metadata for non-existent file_id returns 404."""
    response = client.get("/files/99999/metadata")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_data_404(client):
    """Data for non-existent file_id returns 404."""
    response = client.get("/files/99999/data")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_e2e_upload_then_metadata_then_data(client):
    """
    Key E2E: Upload CSV → GET metadata by id → GET file data by id.
    Validates the full flow and that metadata and data are consistent.
    """
    csv_content = b"name,score\nAlice,100\nBob,99"
    upload_resp = client.post(
        "/files/upload",
        files={"file": ("scores.csv", csv_content)},
    )
    assert upload_resp.status_code == 200, upload_resp.text
    upload_data = upload_resp.json()
    assert upload_data["rows"] == 2
    assert upload_data["cols"] == 2

    # List files and get the created file's id (match by filename from upload response)
    list_resp = client.get("/files/", params={"page": 1, "page_size": 10})
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] >= 1
    uploaded_filename = upload_data["filename"]
    file_id = next(d["id"] for d in list_data["data"] if d["filename"] == uploaded_filename)
    assert isinstance(file_id, int)
    assert file_id >= 1

    # Get metadata by file_id
    meta_resp = client.get(f"/files/{file_id}/metadata")
    assert meta_resp.status_code == 200, meta_resp.text
    meta = meta_resp.json()
    assert meta["id"] == file_id
    assert meta["rows"] == 2
    assert meta["columns"] == 2
    assert meta["filename"]
    assert "uploaded_at" in meta

    # Get file data by file_id (paginated)
    data_resp = client.get(f"/files/{file_id}/data", params={"page": 1, "page_size": 10})
    assert data_resp.status_code == 200, data_resp.text
    data_body = data_resp.json()
    assert "data" in data_body
    assert data_body["total"] == 2
    assert data_body["page"] == 1
    assert data_body["page_size"] == 10
    assert data_body["total_pages"] == 1
    rows = data_body["data"]
    assert len(rows) == 2
    assert rows[0]["name"] == "Alice" and rows[0]["score"] == "100"
    assert rows[1]["name"] == "Bob" and rows[1]["score"] == "99"

    # Optional: second page empty
    page2 = client.get(f"/files/{file_id}/data", params={"page": 2, "page_size": 10})
    assert page2.status_code == 200
    assert page2.json()["data"] == []
    assert page2.json()["total"] == 2
