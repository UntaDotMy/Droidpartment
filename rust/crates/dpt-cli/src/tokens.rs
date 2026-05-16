use std::sync::OnceLock;

use tiktoken_rs::{o200k_base, CoreBPE};

static BPE: OnceLock<Option<CoreBPE>> = OnceLock::new();

fn bpe() -> Option<&'static CoreBPE> {
    BPE.get_or_init(|| o200k_base().ok()).as_ref()
}

/// Count tokens with the o200k_base tokenizer (the encoding used by current
/// frontier chat models). Falls back to a coarse char-rounded estimate if the
/// tokenizer fails to initialize.
pub fn count(s: &str) -> usize {
    if s.is_empty() {
        return 0;
    }
    if let Some(b) = bpe() {
        b.encode_with_special_tokens(s).len()
    } else {
        // Fallback only triggers if the embedded tiktoken vocab fails to load.
        s.chars().count() / 4
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn empty_string_is_zero() {
        assert_eq!(count(""), 0);
    }

    #[test]
    fn known_short_strings() {
        // o200k_base: "hello" is one token.
        assert_eq!(count("hello"), 1);
        // " world" is one token (leading space, common).
        assert_eq!(count(" world"), 1);
    }

    #[test]
    fn whitespace_normalization() {
        // Newlines and tabs each count as tokens.
        let n = count("a\nb\nc\nd");
        assert!(n >= 4, "expected at least 4 tokens, got {n}");
    }

    #[test]
    fn long_text_is_proportional() {
        let s = "the quick brown fox jumps over the lazy dog. ".repeat(50);
        let n = count(&s);
        // ~9 tokens per phrase, 50 repeats -> several hundred.
        assert!(n > 200, "expected >200 tokens, got {n}");
        assert!(n < 2000, "expected <2000 tokens, got {n}");
    }
}
