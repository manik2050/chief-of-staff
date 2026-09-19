# Data rights

Public availability is not training permission.

Record a `SourceRecord` before downloading anything:

- `rights_status` is `approved` or `synthetic_original`, never assumed
- `permission_scope` names whether training is allowed
- commercial use and redistribution are separate flags
- keep permission emails in `data/permissions/` (gitignored)

## What may be public

- source metadata
- file hashes
- processing code
- dataset schemas
- evaluation code
- original synthetic examples we wrote

## What stays private

- raw PDFs
- OCR output
- human gold transcriptions of third-party decks
- permission evidence
- user-submitted data, even with opt-in, until it is reviewed and stripped
