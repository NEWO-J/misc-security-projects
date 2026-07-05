use std::io;
use std::io::Write;

fn main() {
    print!("Enter API key: ");
    let secret_key = String::from("ABC123");
    io::stdout().flush();
    let mut input_key = String::new();
    io::stdin().read_line(&mut input_key).expect("Failed to parse input");

    let result = diff_accumulator(input_key, secret_key);
    print!("{}", result);
}

fn diff_accumulator(input_key: String, secret_key: String) -> bool {
    let mut accumulation = 0;

    let secret_bytes: &[u8] = secret_key.as_bytes();
    let bytes: &[u8] = input_key.trim().as_bytes();
    
    for i in 0..bytes.len() {
            let result = bytes[i] ^ secret_bytes[i];
            accumulation += result;
        }
    
    if accumulation > 0 {
        return false;
    }

    return true;
}
