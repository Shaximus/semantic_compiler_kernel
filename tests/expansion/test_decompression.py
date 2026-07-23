def test_decompress_produces_system_model():
    from semantic_compiler.expansion import decompress
    from semantic_compiler.core.packet import SemanticPacket
    packet = SemanticPacket(raw_input="A firewall protects a network")
    model = decompress(packet)
    assert model["domain"]
    assert "components" in model
    assert "pathology_profile" in model
    assert "advisor" in model
