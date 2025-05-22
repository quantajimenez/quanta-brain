from quanta.brain.ml_brain_boot import boot_brain

def test_boot_brain():
    model = boot_brain(batch_mode=True)
    assert model is not None
    print("✅ ML Brain pipeline test passed.")

if __name__ == "__main__":
    test_boot_brain()
