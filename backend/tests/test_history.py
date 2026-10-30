"""
Automated Backend Scan History Tests
Tests listing, filtering, search, pagination, deleting individual records, and clearing all history.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_history_flow():
    """Test full history recording, retrieval, searching, and deletion cycle."""
    # 1. Perform a scan to ensure at least one record exists
    scan_resp = client.post("/api/scan/url", json={"url": "http://192.168.1.50/login.php"})
    assert scan_resp.status_code == 200
    scan_id = scan_resp.json()["scan_id"]

    # 2. Retrieve history list
    list_resp = client.get("/api/history")
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert "total" in data
    assert "items" in data
    assert data["total"] >= 1

    # Check that our scan_id is present
    ids = [item["scan_id"] for item in data["items"]]
    assert scan_id in ids

    # 3. Test filtering by scan_type
    url_resp = client.get("/api/history?scan_type=url")
    assert url_resp.status_code == 200
    for it in url_resp.json()["items"]:
        assert it["scan_type"] == "url"

    # 4. Test searching
    search_resp = client.get("/api/history?search=192.168.1.50")
    assert search_resp.status_code == 200
    assert any("192.168.1.50" in it["target_preview"] for it in search_resp.json()["items"])

    # 5. Delete individual scan
    del_resp = client.delete(f"/api/history/{scan_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    # 6. Verify non-existent delete returns 404
    del_404 = client.delete("/api/history/non-existent-scan-id-xyz")
    assert del_404.status_code == 404

    # 7. Test clear all
    clear_resp = client.delete("/api/history")
    assert clear_resp.status_code == 200
    assert clear_resp.json()["success"] is True

    # Check empty list
    empty_list = client.get("/api/history")
    assert empty_list.json()["total"] == 0
