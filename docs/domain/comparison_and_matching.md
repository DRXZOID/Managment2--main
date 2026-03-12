# Comparison and Matching

## Purpose

This document defines how comparison works and how matching results are interpreted.

## High-level model

Comparison is built around a reference catalog and one or more mapped target categories.

The system produces four conceptual result classes:

1. confirmed matches
2. candidate groups
3. reference-only items
4. target-only items

## Confirmed matches

Confirmed matches are backed by persisted `ProductMapping` records.

Rules:
- they are treated as trusted matches
- they must appear consistently across repeated comparisons until data changes invalidate them
- confirmation is an explicit action, not an automatic side effect of candidate generation

## Candidate groups

Candidate groups are runtime-only heuristic results.

Rules:
- they are not persisted as truth
- they may include confidence/reasoning metadata
- they are inputs for human review and later confirmation
- they may disappear or change after product data refresh or heuristic changes

## Reference-only items

These are products from the selected reference category scope that have:
- no confirmed mapping
- no acceptable candidate in the selected target scope

## Target-only items

These are products from the selected target category scope that have:
- no confirmed mapping
- no candidate relation to reference products in the selected context

Important:
target-only in comparison output and “gap” in `/gap` are related but not identical concepts.
Gap is a review workflow built on top of target-only logic plus status tracking and context filtering.

## Matching policy

The current project uses domain-oriented heuristics for sports/hockey catalog matching.

At a policy level:
- product type mismatch is a hard negative
- incompatible sports context is a hard negative or a major penalty
- goalie markers, handedness, curve, fit profile and similar domain tokens influence scoring
- normalized text is necessary but not sufficient for a good match

## Persistence policy

Persist:
- confirmed `ProductMapping`

Do not persist as business truth:
- transient candidates
- temporary ranking lists
- ad hoc debugging parse results

## Failure and fallback policy

When mappings do not exist:
- comparison must not proceed as a normal successful flow
- UI should prompt the user to go to `/service`
- API should return a validation error rather than guessing

When data is stale:
- keep the DB-first contract
- direct the user to refresh data operationally
- do not silently replace the contract with live scrape behavior
