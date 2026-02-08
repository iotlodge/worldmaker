# push--3-srv Dockerfile
FROM rust:1.75-slim AS builder
WORKDIR /app
COPY Cargo.toml .
COPY main.rs src/
RUN cargo build --release

FROM debian:bookworm-slim
COPY --from=builder /app/target/release/push--3-srv /usr/local/bin/
EXPOSE 8080
CMD ["push--3-srv"]
