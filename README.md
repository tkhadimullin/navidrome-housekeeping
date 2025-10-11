# Navidrome Housekeeping

**Navidrome Housekeeping** is a small Python utility designed to help clean up unwanted songs from your Navidrome music library by moving them out. The script preserves original file paths, so you can revert any changes if needed. This is intended to work with `ND_SCANNER_PURGEMISSING: always` setting on Navidrome so it auto-purges deleted files.

This project runs as a continuous background task, using the **Navidrome REST API**.

## How It Works

1. Connects to your Navidrome server via API.
2. Queries the library for songs marked with exactly one star
3. Moves matched files from your library (`LIBRARY_DIR`) to a target folder (`TARGET_DIR`), preserving their relative paths.
4. Logs actions and errors for easy troubleshooting.

## Configuration

Configuration is done via environment variables:

| Variable             | Description                                           | Default                    |
| -------------------- | ----------------------------------------------------- | -------------------------- |
| `NAVIDROME_URL`      | Base URL of your Navidrome server *(required)*        |                            |
| `NAVIDROME_USERNAME` | Navidrome username *(required)*                       |                            |
| `NAVIDROME_PASSWORD` | Navidrome password *(required)*                       |                            |
| `TARGET_DIR`         | Folder to move deleted songs to                       | `/deleted_songs`           |
| `LIBRARY_DIR`        | Path to your Navidrome library root                   | `/music`                   |
| `POLL_INTERVAL`      | Polling interval in seconds                           | `60`                       |
| `TARGET_RATING`      | Star rating to target for removal                     | `1`                        |
| `DRY_RUN`            | If true, shows what would happen without moving files | `false`                    |
---

## Running with Docker Compose


```yaml
version: "3.9"
services:
  navidrome:
    image: deluan/navidrome:latest
    container_name: navidrome
    restart: unless-stopped
    environment:
      # ... other settings
      ND_SCANNER_PURGEMISSING: always
    volumes:
      - /path/to/your/music:/music:ro

  navidrome-housekeeping:
    image: wiseowls/navidrome-housekeeping:latest
    container_name: navidrome-housekeeping
    restart: unless-stopped
    environment:
      NAVIDROME_URL: http://navidrome:4533
      NAVIDROME_USERNAME: admin
      NAVIDROME_PASSWORD: secret
      POLL_INTERVAL: 300
    volumes:
      - /path/to/your/music:/music
      - /path/to/your/deleted_songs:/deleted_songs
```

Run with:

```bash
docker-compose up -d
```

This will start the container in the background, polling your Navidrome library every 5 minutes and moving files according to your configuration.

---

## Notes

* Make sure the UID of the container user matches your host user if you want proper file permissions (our Dockerfiles create a user with UID 1000 by default).
* Logs are printed to stdout and can be viewed with `docker logs -f navidrome-housekeeping`.
