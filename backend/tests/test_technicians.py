def test_list_technicians(client):
    """Test listing all technicians."""
    response = client.get("/api/technicians")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3

    tech_ids = [t["technician_id"] for t in data]
    assert "TECH-DXB-01" in tech_ids


def test_list_technicians_availability_filter(client):
    """Test filtering technicians by availability."""
    # Available technicians
    resp_avail = client.get("/api/technicians?available_only=true")
    assert resp_avail.status_code == 200
    avail_data = resp_avail.json()
    assert all(t["availability"] is True for t in avail_data)

    # Unavailable technicians
    resp_unavail = client.get("/api/technicians?available_only=false")
    assert resp_unavail.status_code == 200
    unavail_data = resp_unavail.json()
    assert all(t["availability"] is False for t in unavail_data)
    assert any(t["technician_id"] == "TECH-DXB-03" for t in unavail_data)


def test_get_technician_success(client):
    """Test getting single technician by ID."""
    response = client.get("/api/technicians/TECH-DXB-01")
    assert response.status_code == 200
    data = response.json()
    assert data["technician_id"] == "TECH-DXB-01"
    assert data["name"] == "Ahmed Mansoor"
    assert "HVAC_CERTIFIED" in data["skills"]
    assert "BEARING_OVERHAUL" in data["skills"]
    assert data["experience"] == 8.5
    assert data["availability"] is True


def test_get_technician_not_found(client):
    """Test 404 for unknown technician ID."""
    response = client.get("/api/technicians/TECH-UNKNOWN-99")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
