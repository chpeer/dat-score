# Running DAT Score Calculator Behind a Reverse Proxy

This application is designed to work behind a reverse proxy (like Nginx, Apache, or Traefik). This guide explains how to configure it properly.

## ✅ What Works Out of the Box

- **File uploads** (up to 10MB)
- **Session management**
- **Static file serving**
- **All application functionality**

## 🔧 Configuration Options

### Environment Variables

Set these environment variables to configure proxy behavior:

```bash
# Required: Set a strong secret key
SECRET_KEY=your-super-secret-key-here

# Optional: Enable secure cookies (set to 'true' if proxy provides HTTPS)
SESSION_COOKIE_SECURE=false

# Optional: Enable proxy header trust (set to 'true' for reverse proxy)
PROXY_FIX=true

# Optional: Preferred URL scheme (http or https)
PREFERRED_URL_SCHEME=http
```

## 🚀 Quick Start with Docker Compose

1. **Use the proxy-enabled Docker Compose file:**
   ```bash
   docker-compose -f docker-compose.proxy.yml up --build
   ```

2. **Access the application at:** `http://localhost`

## 🌐 Nginx Configuration

### Basic Configuration (HTTP)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /path/to/dat-score/static/;
        expires 1y;
    }
}
```

### Production Configuration (HTTPS)

See `nginx.conf.example` for a complete HTTPS configuration with SSL.

## 🔒 Security Considerations

### 1. Session Security
- Set `SESSION_COOKIE_SECURE=true` only if your proxy provides HTTPS
- Set `SESSION_COOKIE_HTTPONLY=true` (default)
- Set `SESSION_COOKIE_SAMESITE=Lax` (default)

### 2. Proxy Trust
- Enable `PROXY_FIX=true` only if you trust your reverse proxy
- Ensure your proxy is properly secured
- Use HTTPS in production

### 3. File Upload Security
- The application limits uploads to 10MB
- Files are stored in secure temporary locations
- Files are automatically cleaned up

## 🐳 Docker Deployment

### Option 1: Docker Compose with Nginx
```bash
# Use the provided docker-compose.proxy.yml
docker-compose -f docker-compose.proxy.yml up -d
```

### Option 2: Manual Docker Setup
```bash
# Run the application
docker run -d \
  --name dat-score-app \
  -e SECRET_KEY=your-secret-key \
  -e PROXY_FIX=true \
  -v $(pwd)/word_vector:/app/word_vector:ro \
  -p 5000:5000 \
  dat-score

# Configure your reverse proxy to point to localhost:5000
```

## 🔍 Troubleshooting

### Common Issues

1. **Session not working behind proxy**
   - Ensure `PROXY_FIX=true` is set
   - Check that proxy headers are being forwarded correctly

2. **File uploads failing**
   - Increase `client_max_body_size` in Nginx
   - Check proxy timeout settings

3. **Static files not loading**
   - Verify the `/static/` location in Nginx
   - Check file permissions

4. **HTTPS redirects not working**
   - Set `SESSION_COOKIE_SECURE=true`
   - Configure SSL in your reverse proxy

### Debug Mode
For troubleshooting, you can run the application in debug mode:
```bash
export FLASK_ENV=development
python main.py
```

## 📋 Checklist for Production

- [ ] Set a strong `SECRET_KEY`
- [ ] Configure HTTPS in your reverse proxy
- [ ] Set `SESSION_COOKIE_SECURE=true`
- [ ] Set `PROXY_FIX=true`
- [ ] Configure proper SSL certificates
- [ ] Set up monitoring and logging
- [ ] Configure backup for word vectors
- [ ] Test file upload functionality
- [ ] Verify session persistence

## 🔗 Additional Resources

- [Flask ProxyFix Documentation](https://flask.palletsprojects.com/en/2.3.x/deploying/wsgi-standalone/#proxy-setups)
- [Nginx Reverse Proxy Guide](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)
- [Docker Compose Documentation](https://docs.docker.com/compose/) 