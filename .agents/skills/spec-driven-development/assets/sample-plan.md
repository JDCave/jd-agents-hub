# Implementation Plan: User authentication

**Branch**: `001-add-user-auth` | **Date**: 2026-01-16 | **Spec**: specs/001-add-user-auth/spec.md

**Input**: Feature specification from `/specs/001-add-user-auth/spec.md`

## Summary

Add account creation and sign-in to the existing web surface, reuse the saved-item
store, and persist a 30-day session. The spec decides WHAT; this plan decides HOW.

## Technical Context

**Language/Version**: Python 3.14

**Primary Dependencies**: standard library only

**Storage**: existing saved-item store plus a small account table

**Testing**: unittest

**Target Platform**: Linux server

**Project Type**: web service

**Performance Goals**: sign-in response under 300 ms at the 95th percentile

**Constraints**: no plaintext credential, generic failure message, no client-side scripting requirement

**Scale/Scope**: 10k accounts in the first release

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Principle I (library first): PASS - authentication logic is a standalone module.
- Principle II (CLI interface): N/A for this web surface; the module still exposes a JSON mode.
- Violations: none.

## Phase 0: Outline & Research

- Decision: hash credentials with the standard library's scrypt wrapper.
  Rationale: no external dependency and a memory-hard primitive.
  Alternatives considered: PBKDF2, a third-party password library.

## Phase 1: Design & Contracts

- data-model.md: account and session entities.
- contracts/: sign-in request and response shapes.
- quickstart.md: runnable sign-in validation scenarios.

## Complexity Tracking

No constitution violations, so this section stays empty.
