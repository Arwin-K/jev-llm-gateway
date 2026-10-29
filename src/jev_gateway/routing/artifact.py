"""Validate and reload a trained router without accepting base weights as training."""
import argparse
import json
from pathlib import Path

from .contracts import TIERS


class ArtifactError(RuntimeError):
    pass


def inspect(path: Path, *, settings_fingerprint: str | None = None,
            backend_models: dict[str, str] | None = None) -> dict:
    try:
        metadata = json.loads((path/'metadata.json').read_text())
    except (OSError, ValueError) as exc:
        raise ArtifactError('trained artifact metadata missing or invalid') from exc
    if metadata.get('artifact_kind') != 'trained_distilbert':
        raise ArtifactError('artifact is not a trained DistilBERT router')
    if metadata.get('label2id') != {tier: i for i, tier in enumerate(TIERS)}:
        raise ArtifactError('incompatible label mapping')
    if not metadata.get('train_prompt_ids') or not metadata.get('validation_prompt_ids'):
        raise ArtifactError('training and validation provenance required')
    if settings_fingerprint and metadata.get('settings_fingerprint') != settings_fingerprint:
        raise ArtifactError('generation settings changed; retrain or select compatible artifact')
    if backend_models and metadata.get('backend_models') != backend_models:
        raise ArtifactError('backend model identities changed; retrain or select compatible artifact')
    model_dir = path/'model'
    if not (model_dir/'config.json').is_file() or not (model_dir/'tokenizer_config.json').is_file():
        raise ArtifactError('model or tokenizer configuration missing')
    if not any((model_dir/name).is_file() for name in ('model.safetensors','pytorch_model.bin')):
        raise ArtifactError('trained weights missing')
    return metadata


def reload_model(path: Path, *, device: str = 'cpu'):
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    inspect(path)
    model = AutoModelForSequenceClassification.from_pretrained(path/'model').to(device).eval()
    tokenizer = AutoTokenizer.from_pretrained(path/'model')
    return model, tokenizer


def verify_reload(path: Path, texts: list[str]) -> dict:
    import torch
    metadata = inspect(path)
    model, tokenizer = reload_model(path)
    with torch.inference_mode():
        batch = tokenizer(texts, truncation=True, padding='max_length',
                          max_length=metadata['max_length'], return_tensors='pt')
        probabilities = torch.softmax(model(**batch).logits, dim=-1).tolist()
    return {'texts': len(texts), 'probabilities': probabilities,
            'model': metadata['base_model'], 'revision': metadata['base_revision']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--path', type=Path, required=True)
    args = parser.parse_args(argv)
    print(json.dumps(verify_reload(args.path, ['A short math question.', 'A coding task.']), indent=2))


if __name__ == '__main__':
    main()
