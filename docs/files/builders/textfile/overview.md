---
hide:
  - toc
---
# Text Builders

You can find items using IDs written directly in YAML or maintained in a local or remote text file.

No external service configuration is required for this Builder.

| Builder                     | Description                                                                                 |             Works with Movies              |             Works with Shows             |    Works with Playlists and Custom Sort    |
|:----------------------------|:--------------------------------------------------------------------------------------------|:------------------------------------------:|:----------------------------------------:|:------------------------------------------:|
| [`text`](text.md)           | Reads supported IDs and URLs directly from a YAML scalar, multiline string, or list.        | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`text_file`](text-file.md) | Reads supported IDs and URLs from a local or remote text file while preserving source order. | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
