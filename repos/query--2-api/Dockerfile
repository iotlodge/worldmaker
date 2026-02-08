# query--2-api Dockerfile
FROM rust:1.75-slim AS builder
WORKDIR /app
COPY Cargo.toml .
COPY main.rs src/
RUN cargo build --release

FROM debian:bookworm-slim
COPY --from=builder /app/target/release/query--2-api /usr/local/bin/
EXPOSE 8080
CMD ["query--2-api"]
