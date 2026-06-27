from app.services.attack_pack_loader import AttackPackLoader


def test_attack_pack_loader_counts():
    packs = AttackPackLoader().load_all()
    assert len(packs) >= 9
    assert sum(len(pack.tests) for pack in packs) >= 20
    assert {pack.id for pack in packs} >= {"prompt_injection", "jailbreak", "rag_poisoning"}
