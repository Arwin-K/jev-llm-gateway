"""Optional DistilBERT fine-tuning from private, pre-labeled development rows."""
import argparse
import json
import random
from collections import Counter
from pathlib import Path

from .contracts import TIERS


def _rows(path: Path, split: str):
    from .training_data import TrainingRow
    rows = [TrainingRow(**json.loads(line)) for line in path.read_text().splitlines() if line]
    if not rows or any(row.split != split or row.label not in TIERS for row in rows):
        raise ValueError(f'{path} must contain nonempty {split} labels')
    if len({row.prompt_id for row in rows}) != len(rows):
        raise ValueError('duplicate prompt IDs')
    return rows


def train(train_path: Path, validation_path: Path, output: Path, *, revision: str,
          seed: int = 17, max_length: int = 256, epochs: int = 3,
          learning_rate: float = 2e-5, batch_size: int = 16):
    import numpy as np
    import torch
    from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
                              Trainer, TrainingArguments, set_seed)
    training = _rows(train_path, 'train')
    validation = _rows(validation_path, 'validation')
    if set(r.prompt_id for r in training) & set(r.prompt_id for r in validation):
        raise ValueError('train/validation prompt overlap')
    identities = {tuple(sorted(r.backend_models.items())) for r in training + validation}
    if len(identities) != 1:
        raise ValueError('backend model identities differ across training and validation')
    configs = {r.settings_fingerprint for r in training + validation}
    if len(configs) != 1:
        raise ValueError('generation settings differ across training and validation')
    if not revision or not (0 < max_length <= 512 and epochs > 0 and batch_size > 0 and learning_rate > 0):
        raise ValueError('pin a pretrained revision and positive training settings')
    output.mkdir(parents=True, exist_ok=False)
    set_seed(seed)
    random.seed(seed)
    label2id = {tier: i for i, tier in enumerate(TIERS)}
    tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased', revision=revision)
    model = AutoModelForSequenceClassification.from_pretrained(
        'distilbert-base-uncased', revision=revision, num_labels=3,
        id2label={i: tier for tier, i in label2id.items()}, label2id=label2id)

    class Rows(torch.utils.data.Dataset):
        def __init__(self, values):
            self.encodings = tokenizer([r.text for r in values], truncation=True,
                                       padding='max_length', max_length=max_length)
            self.labels = [label2id[r.label] for r in values]
        def __len__(self): return len(self.labels)
        def __getitem__(self, index):
            return {key: torch.tensor(value[index]) for key, value in self.encodings.items()} | {
                'labels': torch.tensor(self.labels[index])}

    counts = Counter(r.label for r in training)
    weights = torch.tensor([len(training)/(3*counts[t]) if counts[t] else 0 for t in TIERS], dtype=torch.float)

    class WeightedTrainer(Trainer):
        def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
            labels = inputs.pop('labels')
            outputs = model(**inputs)
            loss = torch.nn.functional.cross_entropy(outputs.logits, labels,
                                                      weight=weights.to(outputs.logits.device))
            return (loss, outputs) if return_outputs else loss

    def metrics(prediction):
        predictions = np.argmax(prediction.predictions, axis=1)
        true = prediction.label_ids
        accuracy = float(np.mean(predictions == true))
        f1 = []
        for label in range(3):
            tp = int(np.sum((predictions == label) & (true == label)))
            fp = int(np.sum((predictions == label) & (true != label)))
            fn = int(np.sum((predictions != label) & (true == label)))
            f1.append(2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0.)
        return {'accuracy': accuracy, 'macro_f1': sum(f1)/3}

    args = TrainingArguments(output_dir=str(output/'checkpoints'), seed=seed,
                             per_device_train_batch_size=batch_size,
                             per_device_eval_batch_size=batch_size,
                             learning_rate=learning_rate, num_train_epochs=epochs,
                             eval_strategy='epoch', save_strategy='epoch',
                             load_best_model_at_end=True, metric_for_best_model='macro_f1',
                             greater_is_better=True, report_to='none')
    trainer = WeightedTrainer(model=model, args=args, train_dataset=Rows(training),
                              eval_dataset=Rows(validation), compute_metrics=metrics)
    trainer.train()
    evaluation = trainer.evaluate()
    trainer.save_model(str(output/'model'))
    tokenizer.save_pretrained(str(output/'model'))
    metadata = {'artifact_kind': 'trained_distilbert', 'base_model': 'distilbert-base-uncased',
                'base_revision': revision, 'seed': seed, 'max_length': max_length,
                'truncation': True, 'padding': 'max_length', 'epochs': epochs,
                'learning_rate': learning_rate, 'batch_size': batch_size,
                'checkpoint_rule': 'highest validation macro_f1 at epoch end',
                'train_counts': dict(counts), 'validation_counts': dict(Counter(r.label for r in validation)),
                'label2id': label2id, 'backend_models': dict(identities.pop()),
                'settings_fingerprint': configs.pop(), 'evaluation': evaluation,
                'train_prompt_ids': [r.prompt_id for r in training],
                'validation_prompt_ids': [r.prompt_id for r in validation],
                'source_revisions': sorted({r.source_revision for r in training+validation}),
                'dataset_revisions': sorted({r.dataset_revision for r in training+validation})}
    (output/'metadata.json').write_text(json.dumps(metadata, indent=2, sort_keys=True))
    return metadata


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--train', type=Path, required=True)
    parser.add_argument('--validation', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--seed', type=int, default=17)
    parser.add_argument('--max-length', type=int, default=256)
    parser.add_argument('--epochs', type=int, default=3)
    parser.add_argument('--learning-rate', type=float, default=2e-5)
    parser.add_argument('--batch-size', type=int, default=16)
    args = parser.parse_args(argv)
    train(args.train, args.validation, args.output, revision=args.revision,
          seed=args.seed, max_length=args.max_length, epochs=args.epochs,
          learning_rate=args.learning_rate, batch_size=args.batch_size)


if __name__ == '__main__':
    main()
