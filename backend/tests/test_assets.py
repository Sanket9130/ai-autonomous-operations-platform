def test_list_assets(client):
    """Test retrieving list of assets."""
    response = client.get("/api/assets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Verify presence of CHILLER-MARINA-101
    asset_ids = [a["asset_id"] for a in data]
    assert "CHILLER-MARINA-101" in asset_ids


def test_get_asset_success(client):
    """Test retrieving a specific asset with details and telemetry."""
    response = client.get("/api/assets/CHILLER-MARINA-101")
    assert response.status_code == 200
    data = response.json()
    assert data["asset_id"] == "CHILLER-MARINA-101"
    assert data["name"] == "Chiller Unit Marina 101"
    assert data["asset_type"] == "HVAC_CHILLER"
    assert data["criticality"] == "CRITICAL"
    assert data["latitude"] == 25.0889
    assert data["longitude"] == 55.1458
    assert "latest_telemetry" in data
    assert data["latest_telemetry"]["vibration_rms"] == 4.82


def test_get_asset_not_found(client):
    """Test retrieving non-existent asset returns 404."""
    response = client.get("/api/assets/NON-EXISTENT-999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
