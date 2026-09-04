/*
Matuzalen AGI - Rust Sovereign Authentication Service
Capa de Identidad y Soberania: reconocimiento de autoridad sin contraseñas.

Modulos profesionales implementados:
- WebAuthn/FIDO2 Handler
- Challenge Generator (nonces criptograficos anti-replay)
- Assertion Verifier (estructura para validacion ECDSA P-256)
- Device Fingerprinting
- JWT con tokens de corta duracion + refresh

ADVERTENCIA: La verificacion ECDSA real requiere integrar la public_key del
authenticator y validar la firma con p256/ecdsa. Aqui se simula el flujo
completo para permitir pruebas de integracion sin hardware FIDO2.
*/

use axum::{
    extract::State,
    http::{HeaderMap, StatusCode},
    response::Json,
    routing::{post, get},
    Router,
};
use chrono::{Duration, Utc};
use jsonwebtoken::{decode, encode, DecodingKey, EncodingKey, Header, Validation};
use p256::ecdsa::{Signature, VerifyingKey};
use p256::ecdsa::signature::Verifier;
use rand::{Rng, RngCore};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::{collections::HashMap, sync::Arc};
use tokio::sync::RwLock;
use tower_http::cors::{Any, CorsLayer};
use uuid::Uuid;

// --- Tipos de datos ---

#[derive(Debug, Serialize, Deserialize, Clone)]
struct PublicKeyCredential {
    credential_id: String,
    public_key_der: Vec<u8>,
    counter: u32,
    aaguid: String,
    transports: Vec<String>,
    device_fingerprint: String,
    created_at: i64,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct PasskeyChallenge {
    challenge: String,
    user_id: String,
    origin: String,
    created_at: i64,
    operation: String, // "register" o "login"
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct FidoRegistration {
    user_id: String,
    credential_id: String,
    client_data_json: String,
    attestation_object: String,
    device_fingerprint: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct FidoAssertion {
    user_id: String,
    credential_id: String,
    client_data_json: String,
    authenticator_data: String,
    signature: String,
    device_fingerprint: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct CognitivePayload {
    user_id: String,
    identity_node: String,
    spiritual_profile: String,
    clearance_level: String,
    active_plan_id: String,
    current_vector_state: Vec<f32>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct TokenPair {
    access_token: String,
    refresh_token: String,
    expires_in: i64,
    cognitive_payload: CognitivePayload,
}

#[derive(Debug, Serialize, Deserialize)]
struct Claims {
    sub: String,
    identity_node: String,
    clearance_level: String,
    exp: usize,
    iat: usize,
    jti: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct RefreshTokenRecord {
    user_id: String,
    token_hash: String,
    expires_at: i64,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct RegistrationOptions {
    rp: HashMap<String, String>,
    user: HashMap<String, String>,
    challenge: String,
    pub_key_cred_params: Vec<HashMap<String, i32>>,
    authenticator_selection: HashMap<String, String>,
    timeout: u32,
    attestation: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct AssertionOptions {
    challenge: String,
    allow_credentials: Vec<HashMap<String, String>>,
    user_verification: String,
    timeout: u32,
    rp_id: String,
}

// --- Estado global en memoria (para demo; usar Redis/DB en produccion) ---

type ChallengeStore = Arc<RwLock<HashMap<String, PasskeyChallenge>>>;
type CredentialStore = Arc<RwLock<HashMap<String, Vec<PublicKeyCredential>>>>;
type RefreshTokens = Arc<RwLock<HashMap<String, RefreshTokenRecord>>>;

#[derive(Clone)]
struct AuthState {
    challenges: ChallengeStore,
    credentials: CredentialStore,
    refresh_tokens: RefreshTokens,
    decoding_key: DecodingKey,
}

// --- Configuracion ---

const JWT_SECRET: &[u8] = b"matuzalen_sovereign_jwt_secret_change_in_production";
const ACCESS_TOKEN_TTL_MINUTES: i64 = 15;
const REFRESH_TOKEN_TTL_DAYS: i64 = 7;
const CHALLENGE_TTL_SECONDS: i64 = 120;
const RP_ID: &str = "localhost";
const RP_NAME: &str = "Matuzalen AGI";
const ORIGIN: &str = "http://localhost:8000";

// --- Helpers criptograficos ---

fn hash_token(token: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(token.as_bytes());
    let result = hasher.finalize();
    hex::encode(result)
}

fn generate_random_challenge() -> String {
    let mut bytes = [0u8; 32];
    rand::thread_rng().fill_bytes(&mut bytes);
    base64::encode_config(&bytes, base64::URL_SAFE_NO_PAD)
}

fn now_timestamp() -> i64 {
    Utc::now().timestamp()
}

fn is_expired(created_at: i64, ttl_seconds: i64) -> bool {
    now_timestamp() - created_at > ttl_seconds
}

fn build_cognitive_payload(user_id: &str) -> CognitivePayload {
    let mut rng = rand::thread_rng();
    let vector: Vec<f32> = (0..768).map(|_| rng.gen::<f32>() * 2.0 - 1.0).collect();

    CognitivePayload {
        user_id: user_id.to_string(),
        identity_node: "Usuario:Arquitecto".to_string(),
        spiritual_profile: "Estratega_Dominante".to_string(),
        clearance_level: "Omega".to_string(),
        active_plan_id: Uuid::new_v4().to_string(),
        current_vector_state: vector,
    }
}

fn issue_tokens(user_id: &str, identity_node: &str, clearance: &str) -> (String, String) {
    let now = Utc::now();
    let access_exp = now + Duration::minutes(ACCESS_TOKEN_TTL_MINUTES);
    let refresh_exp = now + Duration::days(REFRESH_TOKEN_TTL_DAYS);
    let jti = Uuid::new_v4().to_string();

    let access_claims = Claims {
        sub: user_id.to_string(),
        identity_node: identity_node.to_string(),
        clearance_level: clearance.to_string(),
        exp: access_exp.timestamp() as usize,
        iat: now.timestamp() as usize,
        jti: jti.clone(),
    };

    let refresh_claims = Claims {
        sub: user_id.to_string(),
        identity_node: identity_node.to_string(),
        clearance_level: clearance.to_string(),
        exp: refresh_exp.timestamp() as usize,
        iat: now.timestamp() as usize,
        jti: Uuid::new_v4().to_string(),
    };

    let access_token = encode(&Header::default(), &access_claims, &EncodingKey::from_secret(JWT_SECRET)).unwrap();
    let refresh_token = encode(&Header::default(), &refresh_claims, &EncodingKey::from_secret(JWT_SECRET)).unwrap();

    (access_token, refresh_token)
}

// --- Device Fingerprinting ---

fn compute_device_fingerprint(headers: &HeaderMap, user_id: &str) -> String {
    let ua = headers
        .get("user-agent")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("unknown");
    let lang = headers
        .get("accept-language")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("unknown");
    let ip = headers
        .get("x-forwarded-for")
        .or_else(|| headers.get("x-real-ip"))
        .and_then(|v| v.to_str().ok())
        .unwrap_or("127.0.0.1");

    let combined = format!("{}:{}:{}:{}", user_id, ua, lang, ip);
    hash_token(&combined)[..24].to_string()
}

fn verify_device_fingerprint(stored: &str, current: &str) -> Result<(), String> {
    // En produccion: permitir variacion controlada, no exigir identidad exacta
    if stored != current {
        return Err("Device fingerprint mismatch".to_string());
    }
    Ok(())
}

// --- WebAuthn / FIDO2 Verifier ---

fn decode_base64url(input: &str) -> Result<Vec<u8>, String> {
    base64::decode_config(input, base64::URL_SAFE_NO_PAD)
        .or_else(|_| base64::decode_config(input, base64::URL_SAFE))
        .or_else(|_| base64::decode_config(input, base64::STANDARD))
        .map_err(|_| "Invalid base64url".to_string())
}

fn sha256_bytes(data: &[u8]) -> Vec<u8> {
    let mut hasher = Sha256::new();
    hasher.update(data);
    hasher.finalize().to_vec()
}

fn parse_client_data_json(client_data_json: &str) -> Result<HashMap<String, serde_json::Value>, String> {
    let bytes = decode_base64url(client_data_json)?;
    let text = String::from_utf8(bytes).map_err(|_| "Invalid UTF-8 in clientDataJSON")?;
    let parsed: HashMap<String, serde_json::Value> = serde_json::from_str(&text)
        .map_err(|_| "Invalid clientDataJSON JSON")?;
    Ok(parsed)
}

fn validate_challenge(client_data: &HashMap<String, serde_json::Value>, expected: &str) -> Result<(), String> {
    let challenge_b64 = client_data
        .get("challenge")
        .and_then(|v| v.as_str())
        .ok_or("Missing challenge")?;

    let decoded = decode_base64url(challenge_b64)?;
    let expected_decoded = decode_base64url(expected)?;

    if decoded != expected_decoded {
        return Err("Challenge mismatch".to_string());
    }
    Ok(())
}

fn validate_origin(client_data: &HashMap<String, serde_json::Value>) -> Result<(), String> {
    let origin = client_data
        .get("origin")
        .and_then(|v| v.as_str())
        .ok_or("Missing origin")?;
    if origin != ORIGIN {
        return Err("Origin mismatch".to_string());
    }
    Ok(())
}

fn validate_rp_id(authenticator_data: &[u8]) -> Result<(), String> {
    if authenticator_data.len() < 37 {
        return Err("Invalid authenticator data length".to_string());
    }
    let rp_id_hash = &authenticator_data[0..32];
    let expected_hash = sha256_bytes(RP_ID.as_bytes());
    if rp_id_hash != expected_hash {
        return Err("rpId hash mismatch".to_string());
    }
    Ok(())
}

fn check_user_flags(authenticator_data: &[u8]) -> Result<(), String> {
    if authenticator_data.len() < 33 {
        return Err("Authenticator data too short".to_string());
    }
    let flags = authenticator_data[32];
    let user_present = flags & 0x01 != 0;
    let user_verified = flags & 0x04 != 0;

    if !user_present {
        return Err("User not present".to_string());
    }
    if !user_verified {
        return Err("User not verified".to_string());
    }
    Ok(())
}

fn cose_to_sec1(cose_key: &[u8]) -> Result<Vec<u8>, String> {
    // COSE_Key format for EC2/P-256:
    // {1: 2, 3: -7, -1: 1, -2: x (32 bytes), -3: y (32 bytes)}
    let value: serde_cbor::Value = serde_cbor::from_slice(cose_key)
        .map_err(|_| "Invalid COSE key CBOR".to_string())?;

    let map = match value {
        serde_cbor::Value::Map(m) => m,
        _ => return Err("COSE key is not a map".to_string()),
    };

    let kty = map.get(&serde_cbor::Value::Integer(1))
        .ok_or("Missing kty")?;
    if !matches!(kty, serde_cbor::Value::Integer(2)) {
        return Err("Unsupported key type".to_string());
    }

    let crv = map.get(&serde_cbor::Value::Integer(-1))
        .ok_or("Missing crv")?;
    if !matches!(crv, serde_cbor::Value::Integer(1)) {
        return Err("Unsupported curve".to_string());
    }

    let x = match map.get(&serde_cbor::Value::Integer(-2)) {
        Some(serde_cbor::Value::Bytes(b)) if b.len() == 32 => b,
        _ => return Err("Missing or invalid x coordinate".to_string()),
    };

    let y = match map.get(&serde_cbor::Value::Integer(-3)) {
        Some(serde_cbor::Value::Bytes(b)) if b.len() == 32 => b,
        _ => return Err("Missing or invalid y coordinate".to_string()),
    };

    let mut sec1 = Vec::with_capacity(65);
    sec1.push(0x04); // uncompressed point
    sec1.extend_from_slice(x);
    sec1.extend_from_slice(y);
    Ok(sec1)
}

fn extract_public_key_from_attestation(attestation_cbor: &[u8]) -> Result<(Vec<u8>, Vec<u8>, String), String> {
    // attestationObject = { "fmt": "...", "attStmt": {...}, "authData": bytes }
    let value: serde_cbor::Value = serde_cbor::from_slice(attestation_cbor)
        .map_err(|_| "Invalid attestation CBOR".to_string())?;

    let map = match value {
        serde_cbor::Value::Map(m) => m,
        _ => return Err("attestation is not a map".to_string()),
    };

    let auth_data = match map.get(&serde_cbor::Value::Text("authData".to_string())) {
        Some(serde_cbor::Value::Bytes(b)) => b,
        _ => return Err("Missing authData".to_string()),
    };

    if auth_data.len() < 37 {
        return Err("authData too short".to_string());
    }

    let flags = auth_data[32];
    let attested = flags & 0x40 != 0;
    if !attested {
        return Err("No attested credential data".to_string());
    }

    // Parse authData attested credential data
    // offset 0-31: rpIdHash, 32: flags, 33-36: signCount
    let mut pos = 37;

    if pos + 16 > auth_data.len() {
        return Err("authData too short for aaguid".to_string());
    }
    let aaguid = &auth_data[pos..pos + 16];
    pos += 16;

    if pos + 2 > auth_data.len() {
        return Err("authData too short for credential id length".to_string());
    }
    let cred_id_len = u16::from_be_bytes([auth_data[pos], auth_data[pos + 1]]) as usize;
    pos += 2;

    if pos + cred_id_len > auth_data.len() {
        return Err("authData too short for credential id".to_string());
    }
    let _credential_id = &auth_data[pos..pos + cred_id_len];
    pos += cred_id_len;

    if pos >= auth_data.len() {
        return Err("Missing credential public key".to_string());
    }

    let cose_key = &auth_data[pos..];
    let public_key = cose_to_sec1(cose_key)?;

    Ok((public_key, auth_data.clone(), format!("{}-{}-{}-{}-{}",
        aaguid[0], aaguid[1], aaguid[2], aaguid[3], aaguid[4])))
}

fn verify_signature(
    public_key: &[u8],
    authenticator_data: &[u8],
    client_data_hash: &[u8],
    signature: &[u8],
) -> Result<(), String> {
    if public_key.len() != 65 || public_key[0] != 0x04 {
        return Err("Invalid public key: expected 65-byte uncompressed SEC1 P-256 point".to_string());
    }
    if signature.len() < 10 {
        return Err("Invalid signature: too short".to_string());
    }

    let verifying_key = VerifyingKey::from_sec1_bytes(public_key)
        .map_err(|_| "Invalid P-256 public key".to_string())?;

    let sig = Signature::from_der(signature)
        .map_err(|_| "Invalid ECDSA signature DER".to_string())?;

    let mut signed = Vec::with_capacity(authenticator_data.len() + client_data_hash.len());
    signed.extend_from_slice(authenticator_data);
    signed.extend_from_slice(client_data_hash);

    verifying_key
        .verify(&signed, &sig)
        .map_err(|_| "ECDSA signature verification failed".to_string())?;

    Ok(())
}

// --- Handlers ---

async fn register_begin(
    State(state): State<AuthState>,
    headers: HeaderMap,
    Json(req): Json<HashMap<String, String>>,
) -> Result<Json<RegistrationOptions>, (StatusCode, String)> {
    let user_id = req.get("user_id").cloned().unwrap_or_else(|| Uuid::new_v4().to_string());
    let challenge = generate_random_challenge();
    let _fingerprint = compute_device_fingerprint(&headers, &user_id);

    state.challenges.write().await.insert(challenge.clone(), PasskeyChallenge {
        challenge: challenge.clone(),
        user_id: user_id.clone(),
        origin: ORIGIN.to_string(),
        created_at: now_timestamp(),
        operation: "register".to_string(),
    });

    let mut rp = HashMap::new();
    rp.insert("name".to_string(), RP_NAME.to_string());
    rp.insert("id".to_string(), RP_ID.to_string());

    let mut user = HashMap::new();
    user.insert("id".to_string(), base64::encode_config(user_id.as_bytes(), base64::URL_SAFE_NO_PAD));
    user.insert("name".to_string(), user_id.clone());
    user.insert("displayName".to_string(), user_id.clone());

    let mut pub_key_params = HashMap::new();
    pub_key_params.insert("type".to_string(), 1); // public-key
    pub_key_params.insert("alg".to_string(), -7); // ES256

    let mut auth_select = HashMap::new();
    auth_select.insert("authenticatorAttachment".to_string(), "platform".to_string());
    auth_select.insert("userVerification".to_string(), "required".to_string());
    auth_select.insert("residentKey".to_string(), "preferred".to_string());

    let options = RegistrationOptions {
        rp,
        user,
        challenge: challenge.clone(),
        pub_key_cred_params: vec![pub_key_params],
        authenticator_selection: auth_select,
        timeout: 120000,
        attestation: "none".to_string(),
    };

    Ok(Json(options))
}

async fn register_finish(
    State(state): State<AuthState>,
    headers: HeaderMap,
    Json(req): Json<FidoRegistration>,
) -> Result<Json<HashMap<String, String>>, (StatusCode, String)> {
    // 1. Decodificar clientDataJSON y validar challenge, origin
    let client_data = parse_client_data_json(&req.client_data_json)
        .map_err(|e| (StatusCode::BAD_REQUEST, e))?;

    let challenge_str = client_data
        .get("challenge")
        .and_then(|v| v.as_str())
        .ok_or((StatusCode::BAD_REQUEST, "Missing challenge".to_string()))?;

    let stored = {
        let store = state.challenges.read().await;
        store.get(challenge_str).cloned()
    };

    let stored = stored.ok_or((StatusCode::UNAUTHORIZED, "Invalid or expired challenge".to_string()))?;

    if is_expired(stored.created_at, CHALLENGE_TTL_SECONDS) {
        state.challenges.write().await.remove(challenge_str);
        return Err((StatusCode::UNAUTHORIZED, "Challenge expired".to_string()));
    }

    validate_challenge(&client_data, &stored.challenge)
        .map_err(|e| (StatusCode::UNAUTHORIZED, e))?;
    validate_origin(&client_data)
        .map_err(|e| (StatusCode::UNAUTHORIZED, e))?;

    // 2. Extraer public_key real del attestation object (CBOR WebAuthn)
    let attestation_bytes = decode_base64url(&req.attestation_object)
        .map_err(|_| (StatusCode::BAD_REQUEST, "Invalid attestation base64".to_string()))?;

    let (public_key, _auth_data, aaguid) = extract_public_key_from_attestation(&attestation_bytes)
        .map_err(|e| (StatusCode::BAD_REQUEST, e))?;

    let credential = PublicKeyCredential {
        credential_id: req.credential_id.clone(),
        public_key_der: public_key,
        counter: 0,
        aaguid,
        transports: vec!["internal".to_string()],
        device_fingerprint: compute_device_fingerprint(&headers, &req.user_id),
        created_at: now_timestamp(),
    };

    // 3. Guardar credencial
    {
        let mut creds = state.credentials.write().await;
        let entry = creds.entry(req.user_id.clone()).or_insert_with(Vec::new);
        if !entry.iter().any(|c| c.credential_id == req.credential_id) {
            entry.push(credential);
        }
    }

    state.challenges.write().await.remove(challenge_str);

    let mut resp = HashMap::new();
    resp.insert("status".to_string(), "registered".to_string());
    resp.insert("credential_id".to_string(), req.credential_id);
    Ok(Json(resp))
}

async fn login_begin(
    State(state): State<AuthState>,
    headers: HeaderMap,
    Json(req): Json<HashMap<String, String>>,
) -> Result<Json<AssertionOptions>, (StatusCode, String)> {
    let user_id = req.get("user_id").cloned().unwrap_or_else(|| Uuid::new_v4().to_string());
    let challenge = generate_random_challenge();
    let _fingerprint = compute_device_fingerprint(&headers, &user_id);

    state.challenges.write().await.insert(challenge.clone(), PasskeyChallenge {
        challenge: challenge.clone(),
        user_id: user_id.clone(),
        origin: ORIGIN.to_string(),
        created_at: now_timestamp(),
        operation: "login".to_string(),
    });

    let creds = state.credentials.read().await;
    let user_creds = creds.get(&user_id).cloned().unwrap_or_default();

    let allow_credentials: Vec<HashMap<String, String>> = user_creds
        .iter()
        .map(|c| {
            let mut m = HashMap::new();
            m.insert("type".to_string(), "public-key".to_string());
            m.insert("id".to_string(), c.credential_id.clone());
            m.insert("transports".to_string(), c.transports.join(","));
            m
        })
        .collect();

    let options = AssertionOptions {
        challenge,
        allow_credentials,
        user_verification: "required".to_string(),
        timeout: 120000,
        rp_id: RP_ID.to_string(),
    };

    Ok(Json(options))
}

async fn login_finish(
    State(state): State<AuthState>,
    headers: HeaderMap,
    Json(req): Json<FidoAssertion>,
) -> Result<Json<TokenPair>, (StatusCode, String)> {
    // 1. Recuperar y validar reto
    let client_data = parse_client_data_json(&req.client_data_json)
        .map_err(|e| (StatusCode::BAD_REQUEST, e))?;

    let challenge_b64 = client_data
        .get("challenge")
        .and_then(|v| v.as_str())
        .ok_or((StatusCode::BAD_REQUEST, "Missing challenge".to_string()))?;

    let stored = {
        let store = state.challenges.read().await;
        store.get(challenge_b64).cloned()
    };

    let stored = stored.ok_or((StatusCode::UNAUTHORIZED, "Invalid or expired challenge".to_string()))?;

    if is_expired(stored.created_at, CHALLENGE_TTL_SECONDS) {
        state.challenges.write().await.remove(challenge_b64);
        return Err((StatusCode::UNAUTHORIZED, "Challenge expired".to_string()));
    }

    validate_challenge(&client_data, &stored.challenge)
        .map_err(|e| (StatusCode::UNAUTHORIZED, e))?;
    validate_origin(&client_data)
        .map_err(|e| (StatusCode::UNAUTHORIZED, e))?;

    // 2. Recuperar credencial del usuario
    let mut creds = state.credentials.write().await;
    let user_creds = creds.get_mut(&req.user_id)
        .ok_or((StatusCode::UNAUTHORIZED, "No credentials for user".to_string()))?;

    let credential = user_creds
        .iter_mut()
        .find(|c| c.credential_id == req.credential_id)
        .ok_or((StatusCode::UNAUTHORIZED, "Unknown credential".to_string()))?;

    // 3. Validar authenticatorData
    let auth_data = decode_base64url(&req.authenticator_data)
        .map_err(|_| (StatusCode::BAD_REQUEST, "Invalid authenticator data".to_string()))?;

    validate_rp_id(&auth_data)
        .map_err(|e| (StatusCode::UNAUTHORIZED, e))?;
    check_user_flags(&auth_data)
        .map_err(|e| (StatusCode::UNAUTHORIZED, e))?;

    // 4. Verificar contador (anti-clonacion)
    let counter = u32::from_be_bytes([auth_data[33], auth_data[34], auth_data[35], auth_data[36]]);
    if counter <= credential.counter {
        return Err((StatusCode::UNAUTHORIZED, "Credential counter mismatch (possible replay)".to_string()));
    }
    credential.counter = counter;

    // 5. Device fingerprinting
    let current_fp = compute_device_fingerprint(&headers, &req.user_id);
    verify_device_fingerprint(&credential.device_fingerprint, &current_fp)
        .map_err(|e| (StatusCode::UNAUTHORIZED, e))?;

    // 6. Verificar firma criptografica
    let client_data_hash = sha256_bytes(&decode_base64url(&req.client_data_json).unwrap_or_default());
    let signature = decode_base64url(&req.signature)
        .map_err(|_| (StatusCode::BAD_REQUEST, "Invalid signature".to_string()))?;

    verify_signature(&credential.public_key_der, &auth_data, &client_data_hash, &signature)
        .map_err(|e| (StatusCode::UNAUTHORIZED, e))?;

    // 7. Limpiar reto
    state.challenges.write().await.remove(challenge_b64);

    // 8. Emitir tokens
    let payload = build_cognitive_payload(&req.user_id);
    let (access_token, refresh_token) = issue_tokens(
        &req.user_id,
        &payload.identity_node,
        &payload.clearance_level,
    );

    {
        let mut rt_store = state.refresh_tokens.write().await;
        rt_store.insert(
            hash_token(&refresh_token),
            RefreshTokenRecord {
                user_id: req.user_id.clone(),
                token_hash: hash_token(&refresh_token),
                expires_at: (Utc::now() + Duration::days(REFRESH_TOKEN_TTL_DAYS)).timestamp(),
            },
        );
    }

    Ok(Json(TokenPair {
        access_token,
        refresh_token,
        expires_in: ACCESS_TOKEN_TTL_MINUTES * 60,
        cognitive_payload: payload,
    }))
}

// --- Legacy endpoints para compatibilidad ---

async fn legacy_challenge(
    State(state): State<AuthState>,
    Json(req): Json<HashMap<String, String>>,
) -> Result<Json<HashMap<String, String>>, (StatusCode, String)> {
    let user_id = req.get("user_id").cloned().unwrap_or_else(|| Uuid::new_v4().to_string());
    let challenge = generate_random_challenge();

    state.challenges.write().await.insert(challenge.clone(), PasskeyChallenge {
        challenge: challenge.clone(),
        user_id,
        origin: ORIGIN.to_string(),
        created_at: now_timestamp(),
        operation: "login".to_string(),
    });

    let mut resp = HashMap::new();
    resp.insert("challenge".to_string(), challenge);
    Ok(Json(resp))
}

async fn legacy_login(
    State(state): State<AuthState>,
    Json(req): Json<HashMap<String, String>>,
) -> Result<Json<TokenPair>, (StatusCode, String)> {
    let user_id = req.get("user_id").cloned().unwrap_or_else(|| "anonymous".to_string());
    let credential_id = req.get("credential_id").cloned().unwrap_or_default();
    let signature = req.get("signature").cloned().unwrap_or_default();

    // Legacy demo path: acepta firma no vacia de longitud razonable
    if signature.len() < 16 {
        return Err((StatusCode::UNAUTHORIZED, "Invalid signature".to_string()));
    }

    // 1. Guardar credential legacy
    {
        let mut creds = state.credentials.write().await;
        let entry = creds.entry(user_id.clone()).or_insert_with(Vec::new);
        if !entry.iter().any(|c| c.credential_id == credential_id) {
            let public_key = (0..65).map(|i| i as u8).collect::<Vec<u8>>();
            entry.push(PublicKeyCredential {
                credential_id,
                public_key_der: public_key,
                counter: 0,
                aaguid: "legacy".to_string(),
                transports: vec!["internal".to_string()],
                device_fingerprint: "legacy".to_string(),
                created_at: now_timestamp(),
            });
        }
    }

    let payload = build_cognitive_payload(&user_id);
    let (access_token, refresh_token) = issue_tokens(&user_id, &payload.identity_node, &payload.clearance_level);

    {
        let mut rt_store = state.refresh_tokens.write().await;
        rt_store.insert(
            hash_token(&refresh_token),
            RefreshTokenRecord {
                user_id: user_id.clone(),
                token_hash: hash_token(&refresh_token),
                expires_at: (Utc::now() + Duration::days(REFRESH_TOKEN_TTL_DAYS)).timestamp(),
            },
        );
    }

    Ok(Json(TokenPair {
        access_token,
        refresh_token,
        expires_in: ACCESS_TOKEN_TTL_MINUTES * 60,
        cognitive_payload: payload,
    }))
}

async fn refresh(
    State(state): State<AuthState>,
    Json(req): Json<HashMap<String, String>>,
) -> Result<Json<TokenPair>, (StatusCode, String)> {
    let refresh_token = req.get("refresh_token").cloned()
        .ok_or((StatusCode::BAD_REQUEST, "Missing refresh_token".to_string()))?;

    let record = {
        let store = state.refresh_tokens.read().await;
        store.get(&hash_token(&refresh_token)).cloned()
    };

    let record = match record {
        Some(r) if r.expires_at > Utc::now().timestamp() => r,
        _ => return Err((StatusCode::UNAUTHORIZED, "Invalid or expired refresh token".to_string())),
    };

    state.refresh_tokens.write().await.remove(&record.token_hash);

    let payload = build_cognitive_payload(&record.user_id);
    let (new_access, new_refresh) = issue_tokens(
        &record.user_id,
        &payload.identity_node,
        &payload.clearance_level,
    );

    {
        let mut rt_store = state.refresh_tokens.write().await;
        rt_store.insert(
            hash_token(&new_refresh),
            RefreshTokenRecord {
                user_id: record.user_id.clone(),
                token_hash: hash_token(&new_refresh),
                expires_at: (Utc::now() + Duration::days(REFRESH_TOKEN_TTL_DAYS)).timestamp(),
            },
        );
    }

    Ok(Json(TokenPair {
        access_token: new_access,
        refresh_token: new_refresh,
        expires_in: ACCESS_TOKEN_TTL_MINUTES * 60,
        cognitive_payload: payload,
    }))
}

async fn verify(
    headers: HeaderMap,
    State(state): State<AuthState>,
) -> Result<Json<Claims>, (StatusCode, String)> {
    let auth_header = headers
        .get("authorization")
        .and_then(|v| v.to_str().ok())
        .ok_or((StatusCode::UNAUTHORIZED, "Missing Authorization header".to_string()))?;

    let token = auth_header.strip_prefix("Bearer ").unwrap_or(auth_header);

    let token_data = decode::<Claims>(
        token,
        &state.decoding_key,
        &Validation::default(),
    )
    .map_err(|_| (StatusCode::UNAUTHORIZED, "Invalid token".to_string()))?;

    Ok(Json(token_data.claims))
}

async fn cognitive_context(headers: HeaderMap) -> Result<Json<CognitivePayload>, (StatusCode, String)> {
    let user_id = headers
        .get("x-user-id")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("anonymous");

    Ok(Json(build_cognitive_payload(user_id)))
}

// --- Main ---

#[tokio::main]
async fn main() {
    let state = AuthState {
        challenges: Arc::new(RwLock::new(HashMap::new())),
        credentials: Arc::new(RwLock::new(HashMap::new())),
        refresh_tokens: Arc::new(RwLock::new(HashMap::new())),
        decoding_key: DecodingKey::from_secret(JWT_SECRET),
    };

    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let app = Router::new()
        .route("/auth/register/begin", post(register_begin))
        .route("/auth/register/finish", post(register_finish))
        .route("/auth/login/begin", post(login_begin))
        .route("/auth/login/finish", post(login_finish))
        .route("/auth/challenge", post(legacy_challenge))
        .route("/auth/login", post(legacy_login))
        .route("/auth/refresh", post(refresh))
        .route("/auth/verify", get(verify))
        .route("/auth/context", get(cognitive_context))
        .layer(cors)
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:9001").await.unwrap();
    println!("[SOBERANIA] Matuzalen AGI Rust Auth Service en 0.0.0.0:9001");
    axum::serve(listener, app).await.unwrap();
}
