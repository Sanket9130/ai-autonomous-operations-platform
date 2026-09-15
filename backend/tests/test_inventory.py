def test_list_inventory(client):
    """Test listing all inventory items."""
    response = client.get("/api/inventory")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    part_ids = [p["part_id"] for p in data]
    assert "PART-BRG-7701" in part_ids


def test_get_inventory_item(client):
    """Test retrieving a specific inventory item by part_id."""
    response = client.get("/api/inventory/PART-BRG-7701")
    assert response.status_code == 200
    data = response.json()
    assert data["part_id"] == "PART-BRG-7701"
    assert data["part_name"] == "Ceramic Ball Bearing Assembly"
    assert data["category"] == "Bearings"
    assert data["current_stock"] == 2
    assert data["minimum_stock"] == 3
    assert data["lead_time"] == 4
    assert data["unit_cost"] == 450.00


def test_get_inventory_not_found(client):
    """Test retrieving non-existent inventory item returns 404."""
    response = client.get("/api/inventory/INVALID-PART")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
