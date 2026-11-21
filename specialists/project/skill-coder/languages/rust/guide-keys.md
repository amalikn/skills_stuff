---
Title: Rust for this operator, part 3 - keys and secrets, from real code
Category: reference
Status: current
Authority: local-supplement
Scope: Human-readable Rust guide for the operator, parts 15 to 19 (enums that carry data, implementing a library's trait, let chains, keeping secrets out of sight, a module split into a folder), from continuum-app's FR-237 and FR-308 code
Last reviewed: 2026-11-21
Summary: >-
  The third part of the operator's Rust guide, from the device-side encryption code built on 2026-11-21: one enum for two kinds of device key, a trait the age library calls back into,
  let chains in a guard, secrets that never reach logs or arguments, and a module that became a folder. Read parts 1 and 2 first.
---

# Rust, from the code you already run (part 3)

Written for: you, learning Rust. Parts 1 and 2 are [guide-basics.md](guide-basics.md) and [guide-services.md](guide-services.md). The code below is from continuum-app at commit d1b08b0.

## Contents

- [15. An enum whose variants carry different data](#15-an-enum-whose-variants-carry-different-data)
- [16. Implementing a library's trait](#16-implementing-a-librarys-trait)
- [17. Let chains: a condition and a pattern in one if](#17-let-chains-a-condition-and-a-pattern-in-one-if)
- [18. Keeping a secret out of sight](#18-keeping-a-secret-out-of-sight)
- [19. A module that became a folder](#19-a-module-that-became-a-folder)
- [20. Further reading](#20-further-reading)

## 15. An enum whose variants carry different data

A device key is either a file key or a Secure Enclave key, and each needs different data. In Python you might use two classes and `isinstance`; in Rust one enum holds both, and `match` makes you
handle every case (`apps/agent/src/device_key.rs`):

```rust
pub enum DeviceKey {
  File(x25519::Identity),
  Enclave { identity: age::plugin::Identity, recipient: String },
}

pub fn recipient(&self) -> String {
  match self {
    Self::File(id) => id.to_public().to_string(),
    Self::Enclave { recipient, .. } => recipient.clone(),   // `..` ignores the other field
  }
}
```

Add a third kind of key and every `match` that forgets it stops compiling: the compiler finds the places you would otherwise have to remember.

## 16. Implementing a library's trait

The age library calls back into your code when a plugin wants to ask the user something. It says what it needs as a trait, `age::Callbacks`; you supply a type that implements it. The Secure Enclave
key has no access control, so ours answers nothing:

```rust
#[derive(Clone)]
struct NoPrompt;
impl age::Callbacks for NoPrompt {
  fn display_message(&self, _: &str) {}
  fn confirm(&self, _: &str, _: &str, _: Option<&str>) -> Option<bool> { None }
  fn request_public_string(&self, _: &str) -> Option<String> { None }
  fn request_passphrase(&self, _: &str) -> Option<age::secrecy::SecretString> { None }
}
```

`struct NoPrompt;` has no fields: it exists only to carry the behaviour. The trait's declaration (`pub trait Callbacks: Clone + Send + Sync + 'static`) is why `#[derive(Clone)]` is needed: a trait can
demand others first.

## 17. Let chains: a condition and a pattern in one if

Edition 2024 lets `&&` join a plain condition and an `if let` (`apps/coordinator/src/userkey/approve.rs`):

```rust
if !in_roster
  && let Some(r) = step_up(&verifier, &h, &who).await
{
  return r;
}
```

Read it as: only when the device is not in the roster, run the sign-in check, and if it returned a refusal, send it. Clippy asked for this form (`collapsible_if`) over an `if` inside an `if`.

## 18. Keeping a secret out of sight

The account key's private half must never reach a log, a file name or a process argument. The age library wraps it in `SecretString`, which prints as `[REDACTED]`; you must call `expose_secret()` on
purpose to read it, which makes every read easy to find with grep:

```rust
use age::secrecy::ExposeSecret;
age::encrypt_and_armor(recipient, secret.to_string().expose_secret().as_bytes())
```

The same idea in shell (`scripts/recovery_key.sh`): the new key travels through a pipe into the vault, never as an argument, because arguments are visible to every process on the machine (`ps`).

## 19. A module that became a folder

`encryption.rs` grew past the project's 400-line limit. It became `encryption/mod.rs` with two children, `rotation.rs` and `pin.rs`. A child module can use its parent's private functions through
`super::`, so nothing had to be made public:

```rust
// apps/agent/src/encryption/rotation.rs
use super::{add_device, device_id, fetch, generation_doc, get_json, open, send};
```

Outside callers still write `crate::encryption::rotate`, because `mod.rs` re-exports it: `pub use rotation::{recover, rotate};`.

## 20. Further reading

- [Defining an enum](https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html) and [traits](https://doc.rust-lang.org/book/ch10-02-traits.html) in the book.
- [Let chains in Rust 2024](https://doc.rust-lang.org/edition-guide/rust-2024/let-chains.html).
- [Separating modules into different files](https://doc.rust-lang.org/book/ch07-05-separating-modules-into-different-files.html).
- [age 0.12.1](https://docs.rs/age/0.12.1/age/) and [secrecy](https://docs.rs/secrecy/latest/secrecy/).

All links checked 2026-11-21 (HTTP 200).
