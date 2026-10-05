from test_quality_release import awaiting_batch, client, headers, receipt


def test_certificate_requires_released_batch(client):
    batch = receipt(client)
    response = client.get(
        f"/api/v1/quality/batches/{batch['id']}/certificate.pdf",
        headers=headers(client, "attp", "attp123"),
    )
    assert response.status_code == 400


def test_released_batch_certificate_is_pdf(client):
    batch = awaiting_batch(client)
    attp = headers(client, "attp", "attp123")
    release = client.post(
        f"/api/v1/quality/batches/{batch['id']}/transition",
        headers=attp,
        json={"to_status": "released", "reason_code": "CCP_PASS", "note": "Đạt"},
    )
    assert release.status_code == 200

    response = client.get(
        f"/api/v1/quality/batches/{batch['id']}/certificate.pdf",
        headers=attp,
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
