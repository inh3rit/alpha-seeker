from datetime import date


def test_list_positions_empty(client):
    """无持仓时返回空列表"""
    response = client.get("/api/positions")
    assert response.status_code == 200
    assert response.json() == []


def test_create_position(client):
    """添加持仓"""
    response = client.post("/api/positions", json={
        "code": "600519",
        "buy_date": "2026-05-01",
        "buy_price": 1800.00,
        "quantity": 100,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "600519"
    assert data["buy_price"] == 1800.00
    assert data["quantity"] == 100
    assert data["status"] == "holding"


def test_update_position(client):
    """更新持仓"""
    # 先创建
    resp = client.post("/api/positions", json={
        "code": "600519",
        "buy_date": "2026-05-01",
        "buy_price": 1800.00,
        "quantity": 100,
    })
    pos_id = resp.json()["id"]

    # 更新
    response = client.put(f"/api/positions/{pos_id}", json={
        "quantity": 200,
        "status": "sold",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 200
    assert data["status"] == "sold"


def test_delete_position(client):
    """删除持仓"""
    resp = client.post("/api/positions", json={
        "code": "600519",
        "buy_date": "2026-05-01",
        "buy_price": 1800.00,
        "quantity": 100,
    })
    pos_id = resp.json()["id"]

    response = client.delete(f"/api/positions/{pos_id}")
    assert response.status_code == 204

    # 确认已删除
    response = client.get("/api/positions")
    assert response.json() == []


def test_update_nonexistent_position(client):
    """更新不存在的持仓返回 404"""
    response = client.put("/api/positions/999", json={"quantity": 200})
    assert response.status_code == 404


def test_delete_nonexistent_position(client):
    """删除不存在的持仓返回 404"""
    response = client.delete("/api/positions/999")
    assert response.status_code == 404
