# misc-security-projects

Everything in this repository was coded by a human (Me), AI was excluded in the coding process for full educational value to myself, and thus these tools are not polished, nor intended for production use.

A grab-bag of small security engineering experiments. cryptography, secure file handling, and low-level/systems code.

## Directory structure

```
misc-security-projects/
├── .github/workflows/
│   └── container_attest.yml                                     # CI: container build + SLSA build provenance
│
├── cryptography/
│   ├── chacha20-poly1305-engine.py  [WIP]                       # ChaCha20-Poly1305 AEAD encryption engine
│   ├── ssh_key_auditor.py                                       # Audits SSH keys for weak/insecure configurations
│   ├── zero-copy-boundary-parser.py                             # Zero-copy streaming boundary parser
│   ├── zero-copy-boundary-parser-with-desynchronization-prevention.py  # + desync-resistant framing
│   ├── zc-boundary-parser-w-desync-prot-and-hmac.py             # + HMAC integrity on top of desync protection
│   ├── merkle_builder/                                          # Rust: SHA-256 merkle tree constructor
│   ├── cloud_secrets_manager/                                   # AES-GCM secret storage, DEKs key-wrapped under a KEK
│   └── software-supplychain-attestation/  [WIP]                 # Build provenance generation + verification
│
├── file-uploads/
│   ├── secure-file-upload-ext-whitelist.py                      # Hardened file upload with extension whitelist
│   ├── secure-file-upload-ext-whitelist+MIME-check.py           # + MIME type validation
│   ├── upload-ext-whitelist+MIME-check+filename-sanitization.py # + filename sanitization
│   └── secure-svg-upload-anti-xxe-detect.py  [WIP]              # SVG upload with XXE detection
│
├── fuzzing/
│   ├── threaded_directory_fuzzer.py                             # Directory brute-forcer (ThreadPoolExecutor)
│   ├── async_directory_fuzzer.py                                # Directory brute-forcer (asyncio + httpx)
│   └── async_s3_bucket_fuzzer.py                                # S3 bucket name enumeration (asyncio + httpx)
│
├── identity/
│   ├── authenticated_socket/                                    # TCP socket authentication with TOTP-based MFA
│   └── secure_containerized_microservices/                      # Containerized auth: FastAPI + nginx + Postgres + Redis
│
├── log-parsing/
│   ├── binary_search_log_parsing.py                             # O(log n) search over timestamp-sorted logs by byte-seeking
│   ├── stream_log_parser.py                                     # Streaming access-log parser, failed-auth extraction
│   ├── csv_parser.py                                            # CSV log parsing
│   └── json_parser.py                                           # JSON-lines log parsing
│
├── low-level/
│   ├── auth-with-timing-side-channel-prevention/                # Rust: constant-time auth (timing-attack safe)
│   ├── integer_overflow_detector.c                              # C: overflow-safe arithmetic checks
│   └── ring_buffer_overrun_detector.py                          # Detects overruns in a ring buffer
│
├── networking/
│   └── encrypted-sockets/                                       # TLS sockets + MITM interceptor demonstrating the protection
│
├── redteam/
│   └── prototype_pollution.py                                   # Client-side prototype pollution → XSS (PortSwigger lab)
│
└── serialization/
    └── secure-serialization-enforcer.py                         # Strips private attributes before pickle serialization
```

## Notes

Certificates and keys are not committed. Projects that terminate TLS
(`identity/secure_containerized_microservices/`, `networking/encrypted-sockets/`) expect
you to generate your own locally:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout server.key -out server.crt -subj "/CN=localhost"
```
