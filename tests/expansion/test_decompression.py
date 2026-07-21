def test_decompress_produces_system_model():
    from expansion import decompress
    from core.packet import SemanticPacket
    packet = SemanticPacket(raw_input="A firewall protects a network")
    model = decompress(packet)
    assert model["domain"]
    assert "components" in model
    assert "pathology_profile" in model
    assert "advisor" in model
