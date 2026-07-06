# misc-security-projects
Everything in this repository was coded by a human (Me), AI was excluded in the coding process for full educational value to myself, 
and thus these tools are not intended for production use.

A grab-bag of small security engineering experiments. cryptography, secure
file handling, and low-level/systems code.

## Directory structure

```
misc-security-projects/
├── cryptography/
│   ├── chacha20-poly1305-engine.py                              # ChaCha20-Poly1305 AEAD encryption engine
│   ├── ssh_key_auditor.py                                       # Audits SSH keys for weak/insecure configurations
│   ├── zero-copy-boundary-parser.py                             # Zero-copy streaming boundary parser
│   ├── zero-copy-boundary-parser-with-desynchronization-prevention.py  # + desync-resistant framing
│   ├── zc-boundary-parser-w-desync-prot-and-hmac.py          # + HMAC integrity on top of desync protection
|   └── merkle_builder/                                       # Rust: SHA256 merkle tree constructor
│
├── fileuploads/
│   ├── secure-file-upload-ext-whitelist.py                   # Hardened file upload with extension whitelist
|   ├── secure-file-upload-ext-whitelist+MIME-check.py        # File upload + extension whitelist + MIME check
|   ├── secure-svg-upload-anti-xxe-detect.py                  # .SVG file upload with XXE detection
|   └── upload-ext-whitelist+MIME-check+filename-sanitization # extension whitelist + MIME check + filename sanitization
│
├── low-level/
│   └── auth-with-timing-side-channel-prevention/               # Rust: constant-time auth (timing-attack safe)
│      
│
└── ring_buffer_overrun_detector.py                             # Detects overruns in a ring buffer
```
