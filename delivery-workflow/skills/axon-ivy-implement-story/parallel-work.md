# Parallel Work

Parallelize independent implementation units when useful.

Safe when:

- neither unit depends on the other's output
- they modify different files
- coordination overhead is low

Keep sequential when outputs depend on each other:

```text
Entity → Repository
Process → Dialog
Component → Tag Library → Form