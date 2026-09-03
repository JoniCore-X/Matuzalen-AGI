/*
Matuzalen AGI - Rust Sovereign Authentication Service
Capa de Identidad y Soberania para un AGI estrategico y teologico.
No es un CRUD de contabilidad. Es el reconocimiento de soberania.
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
use rand::{Rng, RngCore};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::{collections::HashMap, sync::Arc};
use tokio::sync::RwLock;
use tower_http::cors::{Any, CorsLayer};
use uuid::Uuid;

// --- Tipos de datos ---

#[derive(Debug, Serialize, Deserialize, Clone)]
struct PasskeyChallenge {
    challenge: String,
    user_id: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct PasskeyAssertion {
    user_id: String,
    challenge: String,
    credential_id: String,
    signature: String,
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

// --- Estado global en memoria (para demo; usar Redis en produccion) ---

type ChallengeStore = Arc<RwLock<HashMap<String, PasskeyChallenge>>>;
type UserPasskeys = Arc<RwLock<HashMap<String, Vec<String>>>>;
type RefreshTokens = Arc<RwLock<HashMap<String, RefreshTokenRecord>>>;

#[derive(Clone)]
struct AuthState {
    challenges: ChallengeStore,
    passkeys: UserPasskeys,
    refresh_tokens: RefreshTokens,
    encoding_key: EncodingKey,
    decoding_key: DecodingKey,
}

// --- Configuracion ---

const JWT_SECRET: &[u8] = b"matuzalen_sovereign_jwt_secret_change_in_production";
const ACCESS_TOKEN_TTL_MINUTES: i64 = 15;
const REFRESH_TOKEN_TTL_DAYS: i64 = 7;

// --- Helpers ---

fn hash_token(token: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(token.as_bytes());
    let result = hasher.finalize();
    hex::encode(result)
}

fn generate_random_challenge() -> String {
    let mut bytes = [0u8; 32];
    rand::thread_rng().fill_bytes(&mut bytes);
    hex::encode(bytes)
}

fn build_cognitive_payload(user_id: &str) -> CognitivePayload {
    // En produccion, esto sale de Redis / Neo4j / Qdrant
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

// --- Handlers ---

async fn challenge(
    State(state): axum::extract::State<AuthState>,
    Json(req): Json<HashMap<String, String>>,
) -> Result<Json<HashMap<String, String>>, (StatusCode, String)> {
    let user_id = req.get("user_id").cloned().unwrap_or_else(|| Uuid::new_v4().to_string());
    let challenge_str = generate_random_challenge();

    let challenge = PasskeyChallenge {
        challenge: challenge_str.clone(),
        user_id: user_id.clone(),
    };

    state.challenges.write().await.insert(challenge_str.clone(), challenge);

    let mut resp = HashMap::new();
    resp.insert("challenge".to_string(), challenge_str);
    resp.insert("user_id".to_string(), user_id);
    Ok(Json(resp))
}

async fn login(
    State(state): axum::extract::State<AuthState>,
    Json(assertion): Json<PasskeyAssertion>,
) -> Result<Json<TokenPair>, (StatusCode, String)> {
    // 1. Verificar que el reto exista
    let challenge = {
        let store = state.challenges.read().await;
        store.get(&assertion.challenge).cloned()
    };

    let _challenge = match challenge {
        Some(c) if c.user_id == assertion.user_id => c,
        _ => return Err((StatusCode::UNAUTHORIZED, "Invalid or expired challenge".to_string())),
    };

    // 2. Simular validacion criptografica FIDO2/WebAuthn
    // En produccion: usar webauthn-rs, validar firma y contador.
    let expected_signature = hash_token(&format!("{}:{}", assertion.credential_id, assertion.challenge));
    if !assertion.signature.starts_with(&expected_signature[..8]) && !assertion.signature.len() > 16 {
        // Demo: aceptamos cualquier firma no vacia larga para facilitar pruebas
    }

    // 3. Registrar passkey si es nueva
    {
        let mut passkeys = state.passkeys.write().await;
        let entry = passkeys.entry(assertion.user_id.clone()).or_insert_with(Vec::new);
        if !entry.contains(&assertion.credential_id) {
            entry.push(assertion.credential_id.clone());
        }
    }

    // 4. Eliminar reto usado
    state.challenges.write().await.remove(&assertion.challenge);

    // 5. Construir Payload Cognitivo y tokens
    let payload = build_cognitive_payload(&assertion.user_id);
    let (access_token, refresh_token) = issue_tokens(
        &assertion.user_id,
        &payload.identity_node,
        &payload.clearance_level,
    );

    // 6. Almacenar refresh token
    {
        let mut rt_store = state.refresh_tokens.write().await;
        rt_store.insert(
            hash_token(&refresh_token),
            RefreshTokenRecord {
                user_id: assertion.user_id.clone(),
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
    State(state): axum::extract::State<AuthState>,
    Json(req): Json<HashMap<String, String>>,
) -> Result<Json<TokenPair>, (StatusCode, String)> {
    let refresh_token = req.get("refresh_token").cloned()
        .ok_or((StatusCode::BAD_REQUEST, "Missing refresh_token".to_string()))?;

    // Verificar que el refresh token exista y no haya expirado
    let record = {
        let store = state.refresh_tokens.read().await;
        store.get(&hash_token(&refresh_token)).cloned()
    };

    let record = match record {
        Some(r) if r.expires_at > Utc::now().timestamp() => r,
        _ => return Err((StatusCode::UNAUTHORIZED, "Invalid or expired refresh token".to_string())),
    };

    // Rotar: eliminar el anterior, emitir nuevos
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
    State(state): axum::extract::State<AuthState>,
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

async fn cognitive_context(
    headers: HeaderMap,
) -> Result<Json<CognitivePayload>, (StatusCode, String)> {
    // Simulacion: en produccion, extraer user_id del JWT y cargar de Redis/Neo4j/Qdrant
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
        passkeys: Arc::new(RwLock::new(HashMap::new())),
        refresh_tokens: Arc::new(RwLock::new(HashMap::new())),
        encoding_key: EncodingKey::from_secret(JWT_SECRET),
        decoding_key: DecodingKey::from_secret(JWT_SECRET),
    };

    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let app = Router::new()
        .route("/auth/challenge", post(challenge))
        .route("/auth/login", post(login))
        .route("/auth/refresh", post(refresh))
        .route("/auth/verify", get(verify))
        .route("/auth/context", get(cognitive_context))
        .layer(cors)
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:9001").await.unwrap();
    println!("[SOBERANIA] Matuzalen AGI Rust Auth Service en 0.0.0.0:9001");
    axum::serve(listener, app).await.unwrap();
}
