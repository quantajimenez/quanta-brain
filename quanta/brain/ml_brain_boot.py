"""
ML Brain Boot: Entry for initializing and orchestrating Quanta's self-learning logic.
"""

from quanta.crews.langchain_boot import boot_langchain_memory
from quanta.brain.rl.trainer import train_model
from quanta.brain.rl.scorer import score_model
from quanta.brain.rl.evolution import evolve_model
from quanta.brain.rl.diagnostics import run_self_diagnostics
from quanta.brain.model_store import store_model_version
from quanta.brain.logic_history_log import log_logic_history
from quanta.mesh.audit_log import MeshAuditLogger

logger = MeshAuditLogger()

def boot_brain(batch_mode=True):
    """
    Bootstraps ML brain: loads memory, trains model, runs diagnostics, stores version.
    Runs a full pipeline for smoke testing all submodules.
    """
    logger.log_event("BOOT", "ml_brain", "Booting ML Brain and RL pipelines.")
    llm, embeddings, vectorstore = boot_langchain_memory()
    log_logic_history("BOOT", "ML brain booted", "ml_brain_boot.py", "now")

    # --- Start test pipeline ---
    model = train_model(vectorstore, batch=batch_mode)
    score = score_model(model, vectorstore)
    diag_result = run_self_diagnostics(model)
    evolved_model = evolve_model(model)
    store_model_version(evolved_model, meta={"score": score, "diagnostics": diag_result})

    logger.log_event("PIPELINE", "ml_brain", "Test pipeline complete.")
    return evolved_model

if __name__ == "__main__":
    boot_brain()
