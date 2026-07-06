use sha2::{Digest, Sha256};
use std::collections::VecDeque;
use hex;
use std::io;

#[derive(Debug)]
struct Sibling {
    isright: bool,
    hash: String,
}


fn main() {
    
    fn tree_builder(mut leafs : VecDeque<String>) -> VecDeque<String>  {
        let n = leafs.len();
        if n % 2 == 1 {
        leafs.push_back(leafs[n - 1].clone());

        }
        let finished_len = 2 * leafs.len() - 1;
        let mut old_len = 0;
        let mut distance = leafs.len() - old_len;
        let mut leafsnew: VecDeque<String> = VecDeque::new();

        while leafs.len() != finished_len {
            distance = leafs.len() - old_len;
            old_len = leafs.len(); 
            leafsnew.clear();
            for i in (0..distance).step_by(2) {
                let mut hasher = Sha256::new();
                let combo = leafs[i].clone() + &leafs[i + 1];
                hasher.update(combo.trim().as_bytes());
                let result = hasher.finalize();
                leafsnew.push_front(hex::encode(result));
            
            }

            for i in &leafsnew {
                leafs.push_front(i.clone());
            }
        }
        leafs
    }

    fn gen_proof(input_hash : String, tree: VecDeque<String>) -> Vec<Sibling> {
        let mut proof: Vec<Sibling> = Vec::new();
        let mut start = tree.len()/2;
        let mut end = tree.len();
        let mut parent_index = 0;
            for i in start..end {
                if tree[i] == input_hash {
                    if i % 2 == 1 {
                        proof.push(Sibling {
                            isright: true,
                            hash: tree[i + 1].clone(),
                        });
                    } else {
                        proof.push(Sibling {
                            isright: false,
                            hash: tree[i - 1].clone(),
                        });
                    }
                    parent_index = (i - 1) / 2;
                    break;
                }
            }; 


            if parent_index == 0 {
            panic!("ERROR: hash not found in given tree's leaf nodes!");
            }       

            while parent_index > 0 {
                if parent_index % 2 == 1 {
                        proof.push(Sibling {
                            isright: true,
                            hash: tree[parent_index + 1].clone(),
                        });
                    } else {
                        proof.push(Sibling {
                            isright: false,
                            hash: tree[parent_index - 1].clone(),
                        });
                    }
                parent_index = ((parent_index - 1) / 2);
                }


        
        proof
    }
    
    
    let mut leaves: VecDeque<String> = VecDeque::new();

    let mut input = String::new();
    loop {
       input.clear();
       println!("Enter a value - send 'done' to confirm");
       io::stdin().read_line(&mut input).expect("Failed to read line"); 
       let trimmed = input.trim();
       if trimmed == "done" {
        break;
       }

       leaves.push_back(trimmed.to_string());

    }

    for i in 0..leaves.len() {
        let mut hasher = Sha256::new();
        hasher.update(leaves[i].trim().as_bytes());
        let result = hasher.finalize();
        leaves[i] = hex::encode(result);
    }
    let new = tree_builder(leaves);
    println!("{:#?}", new);

    println!("Merkle Root: {}",new[0]);
    
    println!("Enter your hash to generate proof!");
    let mut input = String::new();
    io::stdin().read_line(&mut input).expect("Failed to read line");
    
    let proof = gen_proof(input.trim().to_string(),new);
    println!("{:#?}", proof);

}
