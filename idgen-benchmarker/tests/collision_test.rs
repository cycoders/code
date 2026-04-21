use crate::{benchmark::*, generators::*};

#[test]
fn test_collision_no_crashes() {
    let gens: Vec<Box<dyn IdGenerator>> = vec![Box::new(NanoIdGen::default())];
    let res = collision_bench(&gens, 1000, 1000000);
    let (colls, sim_pct, _) = res[0].clone();
    assert!(colls == 0 || colls < 10);  // rare collisions
    assert!(sim_pct < 1.0);
}

#[test]
fn test_collision_small_space() {
    let prob = theoretical_prob(1000, 10);  // small space
    assert!(prob > 0.0001);
}
