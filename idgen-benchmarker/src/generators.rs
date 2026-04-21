use nanoid;
use ksuid;
use ulid;
use uuid::Uuid;

pub trait IdGenerator {
    fn name(&self) -> &'static str;
    fn generate(&self) -> String;
    fn bits(&self) -> u32;
}

pub struct UuidGen;

impl IdGenerator for UuidGen {
    fn name(&self) -> &'static str {
        "uuid"
    }

    fn generate(&self) -> String {
        Uuid::new_v4().as_simple().to_string()
    }

    fn bits(&self) -> u32 {
        128
    }
}

pub struct UlidGen;

impl IdGenerator for UlidGen {
    fn name(&self) -> &'static str {
        "ulid"
    }

    fn generate(&self) -> String {
        ulid::Ulid::new().to_string()
    }

    fn bits(&self) -> u32 {
        128
    }
}

pub struct KsuidGen;

impl IdGenerator for KsuidGen {
    fn name(&self) -> &'static str {
        "ksuid"
    }

    fn generate(&self) -> String {
        ksuid::Ksuid::generate().to_string()
    }

    fn bits(&self) -> u32 {
        160
    }
}

#[derive(Clone, Default)]
pub struct NanoIdGen {
    size: usize,
}

impl NanoIdGen {
    pub fn new(size: usize) -> Self {
        Self { size }
    }
}

impl IdGenerator for NanoIdGen {
    fn name(&self) -> &'static str {
        "nanoid"
    }

    fn generate(&self) -> String {
        nanoid::nanoid(self.size)
    }

    fn bits(&self) -> u32 {
        (self.size as f64 * 6.0) as u32  // log2(64)
    }
}

pub fn theoretical_prob(n: u64, bits: u32) -> f64 {
    let space = 2f64.powi(bits as i32);
    let lambda = (n as f64 * (n as f64 - 1.0)) / (2.0 * space);
    1.0 - (-lambda).exp()
}
