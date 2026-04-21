use crate::generators::*;

#[test]
fn test_generators_produce_valid_ids() {
    let gens: Vec<Box<dyn IdGenerator>> = vec![
        Box::new(UuidGen),
        Box::new(UlidGen),
        Box::new(KsuidGen),
        Box::new(NanoIdGen::default()),
    ];

    for gen in gens {
        let id = gen.generate();
        assert!(!id.is_empty(), "{} produced empty ID", gen.name());
        assert!(id.len() >= 20, "{} ID too short: {} chars", gen.name(), id.len());
        assert_ne!(id.find(|c: char| !c.is_ascii_alphanumeric() && c != '-' && c != '_'), Some(0));
    }
}

#[test]
fn test_theoretical_prob() {
    assert!(theoretical_prob(1, 128) < 1e-30);
    assert!(theoretical_prob(1_000_000, 20) > 0.0001);
    assert!(theoretical_prob(1_000_000_000, 128) < 1e-10);
}
