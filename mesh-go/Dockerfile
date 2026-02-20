FROM golang:1.23-alpine AS builder
WORKDIR /app
COPY mesh-go/go.mod ./
RUN go mod download
COPY mesh-go ./
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o bin/mesh ./cmd/main.go

FROM alpine:3.21
RUN apk add --no-cache ca-certificates
COPY --from=builder /app/bin/mesh /usr/local/bin/mesh
EXPOSE 9000
CMD ["mesh"]
