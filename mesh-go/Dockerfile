FROM golang:1.22-alpine AS builder
WORKDIR /src
COPY go.mod ./
RUN go mod download
COPY . .
RUN go build -o /out/mesh ./main.go

FROM alpine:3.20
WORKDIR /app
COPY --from=builder /out/mesh /usr/local/bin/mesh
EXPOSE 9000
CMD ["mesh"]
