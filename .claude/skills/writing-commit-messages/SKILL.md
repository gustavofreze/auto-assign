---
name: writing-commit-messages
description: Generates a Conventional Commits message (English, no trailers), and suggests the next semver release tag with the notes for it. Use when asked for a commit message, to write a commit, to split a change into commits, to bump the version, or to suggest a release tag. Also /writing-commit-messages.
---

# Write commit messages

Generates the Conventional Commits message for a staged or proposed change, and on request the next semver release tag
with the notes that go with it. It only produces text, so it never creates a commit, a tag, or a release. Nothing in it
depends on the stack the repository is written in.

Target: the change to describe, or the release to tag, from the request.

## When to use

- A request for a commit message, `/writing-commit-messages`, or splitting a change into commits.
- A request for the next release tag, a version bump, or the notes for a release.

## When NOT to use

- A request to make the commit, create the tag, or perform any other git write. This skill only produces text.
- No concrete change to describe yet: describe a real staged or proposed diff, not an intention.
- A conformance or rule audit of the change: that is `make review` plus the rule files under `.claude/rules/`, not a
  commit message.

## Rules applied

No code rule. Conventional Commits governs the message, semver governs the tag. The format and the gate live in this
skill, the worked examples in `references/commit-examples.md` and `references/release-examples.md`.

## Assembly order

Route on what was asked. The message and the tag are separate flows, and neither one triggers the other.

### Commit message

1. Read the staged or proposed change (the diff).
2. Format `<type>: <Description>` with no scope, an imperative present-tense Description that ends with a period, in
   English. Allowed types: `ci`, `fix`, `feat`, `docs`, `test`, `chore`, `build`, `revert`, `refactor`.
3. Leave the body out. Omitting it is the default, not the exception. See § Body.
4. Split into commits when the change has more than one logical intent.

### Release tag

1. Read the last published tag. Fetching first is the one step that touches the remote, and it is needed only when the
   local clone may be behind it.

   ```bash
   git fetch --tags
   git describe --tags --abbrev=0
   ```

2. Copy that tag's spelling into the next one. A previous `1.3.0` makes the next one `1.3.1` and never `v1.3.1`, and a
   previous `v1.3.0` keeps its `v`. When the repository has published no tag at all, propose `1.0.0` and say that it is
   the first. When the last tag is not semver at all, stop and ask, because there is no bump rule to apply and picking
   one silently changes how the project versions itself.
3. Read every commit that no release contains yet, which is the range from the last published tag to `HEAD`. With no
   tag, read the whole history.

   ```bash
   git log --oneline "$(git describe --tags --abbrev=0)"..HEAD
   ```

4. Pick the bump from that range. A breaking change (a `!` after the type, or a `BREAKING CHANGE` footer) is major, a
   `feat` is minor, anything else is patch. The highest one present decides, so a single `feat` among twenty `chore`
   commits still makes it a minor.
5. Write the bullets from the same range. See § Bullets.
6. Print the tag and the bullets in the final response, and stop there. Do not write a file, do not create the tag, and
   do not open a release.

## Body

The body is omitted by default. A subject that names the type and the change already carries the what, and the diff
carries the rest, so a body that restates either is noise the reader has to wade through.

Write one only when the why would otherwise be lost: a non-obvious cause, a constraint that forced the approach, or a
consequence a reader would not predict from the diff. Never to restate the subject, never to list the files touched,
never to narrate the steps taken, and never to inflate a small change into something that reads as larger.

A body that does exist is one paragraph, three lines at most, wrapped at 72 columns. Needing more than that is a sign
the commit should have been split.

## Bullets

Bullets describe the release, not the log.

- One bullet per change a consumer of this repository would notice. Two commits that build one thing are one bullet.
- Group the mechanical commits into a single line. Ten dependency bumps from a bot are one bullet, not ten.
- Drop what changes nothing outside the repository: formatting, lint fixes, internal renames, CI tweaks, test-only
  commits, and any commit reverted inside the same range.
- Keep the imperative present tense and the trailing period, the same shape as a subject line.
- When nothing survives the filter, say so and still propose the patch bump.

## Completeness gate

Commit message:

- [ ] Right type for the nature of the change.
- [ ] Imperative subject in English: 50-character target, 72 hard limit.
- [ ] No body, unless the why is genuinely absent from both the subject and the diff.
- [ ] Body, where present, is one paragraph of three lines at most.
- [ ] No trailers (no co-author, no tool attribution).
- [ ] One logical intent per commit.

Release tag:

- [ ] The next tag mirrors the spelling of the last published one, prefix included or omitted the same way.
- [ ] The bump is the highest-ranking change in the range, not the most frequent one.
- [ ] Bullets are grouped by change, never copied one for one from the log.
- [ ] Tag and bullets printed in the response, with nothing written to disk and nothing tagged.

## Additional resources

- **`references/commit-examples.md`**: Concrete messages covering feat, fix, refactor, test, chore, build, and a
  proposed multi-intent split.
- **`references/release-examples.md`**: Worked tags covering a first release, a patch, a minor, a major, and a range
  whose commits are all mechanical.

## Does not do

- Does not commit, push, branch, merge, rebase, tag, or publish a release. Only produces text.
