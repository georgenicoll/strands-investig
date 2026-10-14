from huggingface_hub import snapshot_download
from strands_decider.modeling import StrandsDeciderConfig, checkpoint_dir, config_path

from .decider import CHECKPOINT


def run() -> None:
    print(f"Downloading {CHECKPOINT} ...")
    path = checkpoint_dir(CHECKPOINT)
    print(f"  -> cached at {path}")

    config = StrandsDeciderConfig.from_json(config_path(path))
    print(f"Downloading base model {config.base_model} ...")
    base_path = snapshot_download(config.base_model)
    print(f"  -> cached at {base_path}")

    print("\nDone. `strands-investig decider` will now load from the local cache.")
