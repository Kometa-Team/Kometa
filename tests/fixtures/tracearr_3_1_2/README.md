# Tracearr 3.1.2 compatibility fixtures

Synthetic, reduced responses based on the Public API v2 contract at Tracearr tag
`v3.1.2` (commit `ce5581acbfcd8aef6e70fc1a9cc3f1549761227c`):

- [API definitions](https://github.com/connorgallopo/Tracearr/blob/v3.1.2/apps/server/src/routes/publicV2.openapi.ts)
- [Users implementation](https://github.com/connorgallopo/Tracearr/blob/v3.1.2/apps/server/src/routes/publicV2/users.ts)
- [History implementation](https://github.com/connorgallopo/Tracearr/blob/v3.1.2/apps/server/src/routes/publicV2/history.ts)
- [Watched-media implementation](https://github.com/connorgallopo/Tracearr/blob/v3.1.2/apps/server/src/routes/publicV2/watchedMedia.ts)

Each JSON file contains two cursor pages. Unused optional media artwork,
device and quality fields are omitted from history. Values and opaque cursors are
invented; these are not captures from a running server or a full API schema.

Tests cover display names that can be null, linked-account correlation, identity-scoped
history, resume-chain aggregation, cursor pagination, and movie/episode provider
matching. They do not establish live-server compatibility.
