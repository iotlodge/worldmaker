# push--3-gateway Dockerfile
FROM gradle:8.5-jdk21 AS builder
WORKDIR /app
COPY build.gradle.kts .
COPY Application.kt src/main/kotlin/
RUN gradle shadowJar

FROM eclipse-temurin:21-jre
COPY --from=builder /app/build/libs/*-all.jar /app.jar
EXPOSE 8080
CMD ["java", "-jar", "/app.jar"]
