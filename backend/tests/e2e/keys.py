"""Generate local-only test keys. Nothing here is a real Supabase secret.

Writes: rsa_private.pem, jwks.json, env.sh (PostgREST HS256 secret + service/anon keys)."""
import json
import secrets
import sys
import time
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwk, jwt

out = Path(sys.argv[1])
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
pem = key.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption(),
)
(out / "rsa_private.pem").write_bytes(pem)
public = jwk.construct(
    key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    ),
    "RS256",
).to_dict()
public.update({"kid": "p0-01-local", "use": "sig", "alg": "RS256"})
public = {k: (v.decode() if isinstance(v, bytes) else v) for k, v in public.items()}
(out / "jwks.json").write_text(json.dumps({"keys": [public]}))

hs = secrets.token_urlsafe(48)
exp = int(time.time()) + 6 * 3600
service = jwt.encode({"role": "service_role", "iss": "supabase", "exp": exp}, hs, "HS256")
anon = jwt.encode({"role": "anon", "iss": "supabase", "exp": exp}, hs, "HS256")
(out / "env.sh").write_text(
    f"export PGRST_JWT_SECRET='{hs}'\n"
    f"export SUPABASE_SERVICE_ROLE_KEY='{service}'\n"
    f"export SUPABASE_ANON_KEY='{anon}'\n"
)
print("local test keys written")
