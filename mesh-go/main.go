package main

import (
    "context"
    "encoding/json"
    "log"
    "net/http"
    "os"

    "github.com/redis/go-redis/v9"
)

type Event struct {
    Topic   string `json:"topic"`
    Payload string `json:"payload"`
}

func main() {
    redisURL := getenv("REDIS_URL", "redis://localhost:6379/0")
    addr := getenv("PORT", "9000")

    opt, err := redis.ParseURL(redisURL)
    if err != nil {
        log.Fatal(err)
    }
    client := redis.NewClient(opt)
    ctx := context.Background()

    http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        _ = json.NewEncoder(w).Encode(map[string]string{"status": "ok", "service": "mesh-go"})
    })

    http.HandleFunc("/publish", func(w http.ResponseWriter, r *http.Request) {
        if r.Method != http.MethodPost {
            w.WriteHeader(http.StatusMethodNotAllowed)
            return
        }
        var e Event
        if err := json.NewDecoder(r.Body).Decode(&e); err != nil {
            w.WriteHeader(http.StatusBadRequest)
            _ = json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
            return
        }
        if e.Topic == "" {
            e.Topic = "nexus.mesh.events"
        }
        if err := client.Publish(ctx, e.Topic, e.Payload).Err(); err != nil {
            w.WriteHeader(http.StatusBadGateway)
            _ = json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
            return
        }
        _ = json.NewEncoder(w).Encode(map[string]bool{"published": true})
    })

    log.Printf("mesh-go listening on :%s", addr)
    log.Fatal(http.ListenAndServe(":"+addr, nil))
}

func getenv(k, d string) string {
    if v := os.Getenv(k); v != "" {
        return v
    }
    return d
}
