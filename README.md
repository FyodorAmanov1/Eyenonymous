# EyeNonymous - Privacy-first Edge Video Intelligence

**HackSeoul 2025** | Privacy-first edge video intelligence platform

Jetson processes live camera feed, detects people/scenes, censors sensitive areas on-device, and sends only the blurred/video-safe stream + detection metadata to a web dashboard. Raw video never leaves the edge.

## Architecture

- **Edge (Jetson Nano)**: Grabs camera feed, runs YOLO detection, blurs faces/people, pushes censored RTSP stream
- **Streaming Relay (Node/Express)**: Pulls Jetson RTSP, converts to WebSocket/browser-friendly stream
- **Web App (Next.js)**: Dashboard with `/live`, `/events`, `/analytics`, `/admin` pages
- **Database (Neon Postgres)**: Stores detection metadata

## Getting Started

### Prerequisites

- Node.js 18+ 
- PostgreSQL database (Neon recommended)
- Jetson Nano with RTSP server running (optional for development)

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL="postgresql://user:password@localhost:5432/eyenonymous?sslmode=require"

# RTSP Stream Relay Server
JETSON_RTSP_URL="rtsp://192.168.0.150:8554/unicast"
RELAY_PORT=3001

# Next.js Public Environment Variables
NEXT_PUBLIC_RELAY_HOST="http://localhost:3001"

# API Security (for /api/detections endpoint)
# Shared secret for Jetson device authentication (required in production)
DEVICE_SECRET="your-secret-key-here"

# Rate Limiting (optional, defaults shown)
RATE_LIMIT_WINDOW_MS=60000  # Rate limit window in milliseconds (default: 60000 = 1 minute)
RATE_LIMIT_MAX_REQUESTS=60  # Max requests per window (default: 60)
```

### Installation

```bash
npm install
```

### Database Setup

```bash
# Generate Prisma client
npm run prisma:gen

# Run migrations
npm run prisma:migrate
```

### Running the Application

**Terminal 1 - Next.js dev server:**
```bash
npm run dev
```

**Terminal 2 - RTSP relay server:**
```bash
npm run stream:dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

## Features

- ✅ Real-time video streaming (blurred/censored)
- ✅ Detection metadata tracking
- ✅ Multi-language support (English, Korean)
- ✅ Light/Dark theme
- ✅ Responsive design (mobile & desktop)
- ✅ Modern animations & interactions
- ✅ Performance optimized with React Query

## Project Structure

```
src/
├── app/              # Next.js app router pages
│   ├── (dashboard)/ # Dashboard routes
│   └── api/         # API routes
├── components/       # React components
├── lib/             # Utilities (Prisma, i18n)
├── providers/        # Context providers (Theme, Query, i18n)
└── messages/        # i18n translation files
```

## API Endpoints

### POST /api/detections
Receive detection data from Jetson device.

**Authentication:**
- Requires `X-Device-Secret` header matching `DEVICE_SECRET` environment variable
- If `DEVICE_SECRET` is not set, all requests are allowed (development mode)

**Rate Limiting:**
- Default: 60 requests per minute per device/IP
- Configurable via `RATE_LIMIT_WINDOW_MS` and `RATE_LIMIT_MAX_REQUESTS`
- Rate limit headers included in all responses:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

**Request Body:**
```json
{
  "deviceId": "jetson-001",
  "scene": "office",
  "labels": [
    { "name": "person", "conf": 0.95 },
    { "name": "laptop", "conf": 0.87 }
  ]
}
```

**Example (cURL):**
```bash
curl -X POST http://localhost:3000/api/detections \
  -H "Content-Type: application/json" \
  -H "X-Device-Secret: your-secret-key-here" \
  -d '{"deviceId":"jetson-001","labels":[{"name":"person","conf":0.95}]}'
```

### GET /api/detections
Fetch detection history.

**Query Parameters:**
- `limit` (optional): Number of detections to return (default: 50, max: 200)

**Example:**
```bash
curl http://localhost:3000/api/detections?limit=20
```

## Built With

- [Next.js 16](https://nextjs.org) - React framework
- [React Query](https://tanstack.com/query) - Data fetching
- [Prisma](https://prisma.io) - Database ORM
- [next-intl](https://next-intl-docs.vercel.app) - Internationalization
- [Tailwind CSS v4](https://tailwindcss.com) - Styling
- [rtsp-relay](https://github.com/k-yle/rtsp-relay) - RTSP to WebSocket

## Team

Firdavs • Pulin • Azizbek • Prithwis
