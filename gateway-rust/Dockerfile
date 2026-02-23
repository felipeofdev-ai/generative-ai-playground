FROM rust:1.82-slim AS builder

WORKDIR /app
COPY gateway-rust/Cargo.toml ./
COPY gateway-rust/src ./src

RUN apt-get update && apt-get install -y --no-install-recommends pkg-config libssl-dev && rm -rf /var/lib/apt/lists/*
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/target/release/gateway /usr/local/bin/gateway
EXPOSE 8080
CMD ["gateway"]
