FROM golang:1.24-alpine AS builder
WORKDIR /app
COPY service/go.mod service/go.sum ./
RUN go mod download
COPY service/ .
RUN CGO_ENABLED=0 GOOS=linux go build -o /reviewer main.go

FROM alpine:latest
RUN apk update && apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /reviewer .
EXPOSE 8080
CMD ["./reviewer"]