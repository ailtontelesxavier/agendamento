def test_create_app_registers_expected_routes(app):
    paths = {route.path for route in app.routes}

    assert "/" in paths
    assert "/appointments" in paths
    assert "/whatsapp/webhook" in paths
    assert "/stats" in paths
