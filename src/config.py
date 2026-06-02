from __future__ import annotations

from dataclasses import asdict, dataclass

FEATURE_IMAGE_SIZE = 32


@dataclass
class TrainConfig:
    data_dir: str = "data/cell_images"
    image_size: int = FEATURE_IMAGE_SIZE
    model_type: str = "svm"
    seed: int = 42
    train_split: float = 0.8
    val_split: float = 0.1
    test_split: float = 0.1
    artifacts_dir: str = "artifacts"
    model_dir: str = "models"
    model_name: str = "malaria_ml.joblib"

    @classmethod
    def from_args(cls, args) -> "TrainConfig":
        return cls(
            data_dir=args.data_dir,
            model_type=args.model_type,
            seed=args.seed,
            artifacts_dir=args.artifacts_dir,
            model_dir=args.model_dir,
            model_name=args.model_name,
        )

    def asdict(self) -> dict:
        return asdict(self)
