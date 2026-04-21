use crate::{benchmark::*, generators::*, table};

#[test]
fn test_speed_small() {
    let gens: Vec<Box<dyn IdGenerator>> = vec![Box::new(UuidGen)];
    let res = speed_bench(&gens, 100, 1);
    assert_eq!(res.len(), 1);
    let (_, time, ips, len) = &res[0];
    assert!(*time > 0.0);
    assert!(*ips > 0.0);
    assert_eq!(*len, 32);
}

#[test]
fn test_mono_small() {
    let gens: Vec<Box<dyn IdGenerator>> = vec![Box::new(UlidGen)];
    let res = mono_bench(&gens, 100, 1);
    assert!((res[0].1 - 100.0).abs() < 20.0);  // roughly high
}
