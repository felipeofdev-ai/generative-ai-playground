use axum::{
    body::Body,
    extract::{Request, State},
    http::{HeaderMap, HeaderValue, StatusCode},
    middleware::{self, Next},
    response::{IntoResponse, Response},
    routing::any,
    Router,
};
use std::{sync::Arc, time::Instant};
use tokio::net::TcpListener;
use tower::ServiceBuilder;
use tower_http::{cors::{Any, CorsLayer}, trace::TraceLayer};
use tracing::{error, info, warn};

#[derive(Debug, Clone)]
struct Config {
    upstream_url: String,
    redis_url: String,
    port: u16,
    default_rpm: u64,
}

impl Config {
    fn from_env() -> Self {
        Self {
            upstream_url: std::env::var("UPSTREAM_URL").unwrap_or_else(|_| "http://localhost:8000".to_string()),
            redis_url: std::env::var("REDIS_URL").unwrap_or_else(|_| "redis://localhost:6379".to_string()),
            port: std::env::var("PORT").unwrap_or_else(|_| "8080".to_string()).parse().unwrap_or(8080),
            default_rpm: std::env::var("DEFAULT_RPM").unwrap_or_else(|_| "60".to_string()).parse().unwrap_or(60),
        }
    }
}

#[derive(Clone)]
struct AppState {
    config: Config,
    http_client: reqwest::Client,
    redis: redis::Client,
}

async fn check_rate_limit(redis: &redis::Client, key: &str, limit: u64) -> Result<(bool, u64), Box<dyn std::error::Error + Send + Sync>> {
    let mut conn = redis.get_multiplexed_async_connection().await?;
    let now_ms = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH)?.as_millis() as u64;
    let window_ms = 60_000u64;
    let script = redis::Script::new(r#"
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
        local count = redis.call('ZCARD', key)
        if count < limit then
            redis.call('ZADD', key, now, now)
            redis.call('EXPIRE', key, math.ceil(window / 1000))
            return {1, limit - count - 1}
        end
        return {0, 0}
    "#);
    let result: Vec<u64> = script.key(key).arg(limit).arg(window_ms).arg(now_ms).invoke_async(&mut conn).await?;
    Ok((result[0] == 1, result[1]))
}

async fn rate_limit_middleware(State(state): State<Arc<AppState>>, req: Request, next: Next) -> Response {
    let path = req.uri().path();
    if path == "/health" || path == "/health/live" {
        return next.run(req).await;
    }

    let tenant_id = req.headers().get("X-Tenant-ID").and_then(|v| v.to_str().ok()).unwrap_or("anonymous");
    let rate_key = format!("nexus:ratelimit:{}", tenant_id);

    match check_rate_limit(&state.redis, &rate_key, state.config.default_rpm).await {
        Ok((allowed, remaining)) => {
            if !allowed {
                warn!("rate_limit_exceeded tenant={}", tenant_id);
                let mut resp = Response::new(Body::from(r#"{"detail":"Rate limit exceeded","retry_after":60}"#));
                *resp.status_mut() = StatusCode::TOO_MANY_REQUESTS;
                resp.headers_mut().insert("Content-Type", HeaderValue::from_static("application/json"));
                return resp;
            }
            let mut response = next.run(req).await;
            response.headers_mut().insert("X-RateLimit-Remaining", HeaderValue::from_str(&remaining.to_string()).unwrap_or(HeaderValue::from_static("0")));
            response
        }
        Err(e) => {
            error!("rate_limit_check_failed error={}", e);
            next.run(req).await
        }
    }
}

async fn proxy_handler(State(state): State<Arc<AppState>>, req: Request) -> impl IntoResponse {
    let start = Instant::now();
    let method = req.method().clone();
    let path_and_query = req.uri().path_and_query().map(|pq| pq.as_str()).unwrap_or("/");
    let upstream = format!("{}{}", state.config.upstream_url, path_and_query);

    let headers = req.headers().clone();
    let body_bytes = axum::body::to_bytes(req.into_body(), usize::MAX).await.unwrap_or_default();

    let mut upstream_req = state.http_client.request(method, &upstream);
    for (name, value) in headers.iter() {
        if name != axum::http::header::HOST {
            upstream_req = upstream_req.header(name, value);
        }
    }
    upstream_req = upstream_req.header("X-Forwarded-By", "nexusai-gateway/3.0");

    match upstream_req.body(body_bytes).send().await {
        Ok(resp) => {
            let status = StatusCode::from_u16(resp.status().as_u16()).unwrap_or(StatusCode::OK);
            let mut out_headers = HeaderMap::new();
            for (name, value) in resp.headers() {
                out_headers.insert(name, value.clone());
            }
            out_headers.insert("X-Gateway-Latency-MS", HeaderValue::from_str(&format!("{:.2}", start.elapsed().as_millis())).unwrap_or(HeaderValue::from_static("0")));
            let body = resp.bytes().await.unwrap_or_default();
            (status, out_headers, body).into_response()
        }
        Err(e) => {
            error!("upstream_error path={} error={}", path_and_query, e);
            (StatusCode::BAD_GATEWAY, format!(r#"{{"detail":"Upstream unavailable","error":"{}"}}"#, e)).into_response()
        }
    }
}

async fn health() -> impl IntoResponse {
    r#"{"status":"ok","service":"nexusai-gateway","version":"3.0.0"}"#
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt().with_env_filter(std::env::var("RUST_LOG").unwrap_or_else(|_| "info,tower_http=warn".to_string())).json().init();

    let config = Config::from_env();
    let port = config.port;
    let http_client = reqwest::Client::builder().timeout(std::time::Duration::from_secs(120)).pool_max_idle_per_host(100).build().expect("Failed to build HTTP client");
    let redis_client = redis::Client::open(config.redis_url.as_str()).expect("Failed to connect to Redis");

    let state = Arc::new(AppState { config, http_client, redis: redis_client });

    let app = Router::new()
        .route("/health", axum::routing::get(health))
        .route("/health/live", axum::routing::get(health))
        .fallback(any(proxy_handler))
        .layer(
            ServiceBuilder::new()
                .layer(TraceLayer::new_for_http())
                .layer(CorsLayer::new().allow_origin(Any).allow_methods(Any).allow_headers(Any))
                .layer(middleware::from_fn_with_state(state.clone(), rate_limit_middleware)),
        )
        .with_state(state);

    let listener = TcpListener::bind(format!("0.0.0.0:{}", port)).await.expect("Failed to bind port");
    info!("nexusai-gateway listening on 0.0.0.0:{}", port);
    axum::serve(listener, app).await.expect("Server error");
}
