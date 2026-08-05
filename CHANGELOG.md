# Changelog

All notable changes to `tnzapi` are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows [`VERSIONS.md`](VERSIONS.md)'s policy.

## [Unreleased]

### Added
- `tnzapi.models` — a shallow, flat re-export of every v300 request/response class, for consumers who want a single import path to type-hint against instead of the internal `tnzapi.api.v300....dtos...` package structure.
- `Contact`/`Group`/`OptOut`'s `Create()`/`Update()` now accept the corresponding `*Response` instance (e.g. what `Detail()`/`Search()` returned) directly for `model=`, projecting it down to only the writable fields.
- `Contact`/`Group`/`OptOut`'s `Update()`/`Delete()` now accept a `*Response` instance in place of a plain ID, extracting the record's id automatically.

### Changed
- Every public v300 response/request class had its `DTO` suffix dropped (e.g. `SMSResponseDTO` → `SMSResponse`, `ContactRequestDTO` → `ContactRequest`) — the old name still works and still resolves to the exact same class, but now emits a `DeprecationWarning` pointing at the new name.

## [3.0.0.0]

Initial `v3.00` JSON API support (Bearer-token auth), alongside continued support for the pre-2.0.3 method-call API (`.Send`/`.Get`/`.Set`, wrapping the older `v2.04` REST API). See [`README.md`](README.md) for the full usage guide and [`.docs/architecture.md`](.docs/architecture.md) for how the two API generations coexist in this codebase.