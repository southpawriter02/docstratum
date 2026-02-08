# DS-AP-ECO-002: Phantom Links

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-ECO-002 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Registry ID** | AP-ECO-002 |
| **Category** | Ecosystem |
| **Check ID** | CHECK-024 |
| **Severity Impact** | Ecosystem-level — affects EcosystemScore rather than per-file QualityScore |
| **Provenance** | v0.0.7 §6 (Ecosystem Anti-Patterns) |

## Description

Phantom Links occur when more than 30% of the links in `llms.txt` reference files that don't exist or return errors. The index promises content that isn't present in the ecosystem. This creates a false sense of completeness while actually delivering broken navigation.

This is severely harmful to LLM agents because they operate under token constraints. An agent following a broken link wastes tokens resolving a path to nowhere, then must handle the error gracefully or backtrack. When 30%+ of links are broken, the agent experiences cumulative token waste and loses trust in the index as a reliable guide. The agent may abandon structured navigation entirely, reverting to less efficient unstructured exploration.

## Detection Logic

```python
def detect_phantom_links(llms_txt_path: str) -> bool:
    """
    Detect if >30% of links in llms.txt are broken.
    
    Returns True if (broken_links / total_links) > 0.30
    """
    if not file_exists(llms_txt_path):
        return False
    
    content = read_file(llms_txt_path)
    all_links = extract_all_links(content)  # Local and external
    
    if len(all_links) == 0:
        return False  # No links to break
    
    broken_count = 0
    for link in all_links:
        if is_external_url(link):
            # Try to resolve external link
            if not url_reachable(link):
                broken_count += 1
        else:
            # Local file reference
            if not file_exists(link):
                broken_count += 1
    
    breakage_ratio = broken_count / len(all_links)
    return breakage_ratio > 0.30
```

## Example (Synthetic)

```markdown
# LLM Ecosystem Index

## Core Documentation

- [Getting Started](./docs/getting-started.md) — Entry point
- [API Reference](./docs/api-reference.md) — Endpoint specifications
- [Advanced Guide](./docs/advanced/guide.md) — Deep dives
- [FAQ](./docs/faq.md) — Common questions
- [Architecture](./docs/architecture.md) — System design

## Supplements

- [Changelog](./CHANGELOG.md)
- [Contributing](./CONTRIBUTING.md)
- [License](./LICENSE.md)
```

In this example, if files `./docs/getting-started.md`, `./docs/advanced/guide.md`, and `./CHANGELOG.md` don't actually exist, then 3 out of 6 links are broken (50% breakage > 30% threshold). Trigger.

## Remediation

1. **Audit all links**: Use a link validator to identify which references are broken.
2. **Remove phantom links**: Delete entries that reference non-existent files.
3. **Create missing files**: If links point to planned content, either create stub files or defer them to a future version.
4. **Use link anchors carefully**: Ensure that internal anchors (e.g., `#section-id`) match actual headings in linked files.
5. **Validate in CI/CD**: Add automated checks to prevent broken links from being committed.

## Affected Criteria

Ecosystem-level diagnostic — no per-file VC criterion. This anti-pattern affects EcosystemScore scoring, not individual QualityScore metrics.

## Emitted Diagnostics

- **DS-DC-W012** (BROKEN_CROSS_FILE_LINK) — Fired when cross-file references cannot be resolved.

## Related Anti-Patterns

- **DS-AP-CRIT-004** (Link Void) — Per-file pattern where individual sections contain broken links. Phantom Links operates at the ecosystem index level.
- **DS-AP-ECO-001** (Index Island) — No links at all vs. broken links. Both isolate the ecosystem from navigation.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
