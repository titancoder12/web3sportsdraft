# Player Development Platform (PDP)

## Overview

The Player Development Platform (PDP) is a Django-based system for tracking youth baseball training and performance. It serves as the foundation for a larger Web3 Baseball Platform that will introduce tokens, NFTs, and blockchain-based data verification.

## Core Features

### Game Logging

- API: `POST /api/v1/game/log`
- Game data stored in PostgreSQL with optional Solana blockchain references
- Events include batting, pitching, and play-by-play updates
- Supports offline mode with sync capability

### Player Stats

- API: `GET /api/v1/player/stats/{player_id}`
- Calculated from game logs
- Permission-based access control

### Coach Evaluations

- Structured periodic assessments
- Practice & training log entries
- Accessible by player and associated coaches

### Token Rewards ($BASEBALL)

- SPL token on Solana blockchain
- Earned through performance and engagement
- API: `POST /api/v1/token/transfer`
- Balance display and reward triggers

### NFT Achievements

- API: `POST /api/v1/nft/mint`
- NFTs for major milestones (e.g., grand slam, MVP)
- Stored on Solana with metadata on IPFS/Arweave

### Verified Performance Profile (VPP)

- NFT issued by approved training centers
- Summary of verified stats, percentile rankings, and evaluations
- Physical baseball card integration with QR code

## Tech Stack

### Backend

- Django + Django REST Framework
- PostgreSQL + Redis (caching)
- Celery for task queue
- PySolana for blockchain integration

### Authentication

- JWT (SimpleJWT)
- Solana Wallet Login (Phantom, Solflare, Backpack)

### Infrastructure

- DigitalOcean Droplet
- Managed PostgreSQL
- Swagger / DRF Spectacular for API documentation

## User Roles

### Player

- View personal stats
- Control data visibility
- Claim NFTs
- Earn tokens

### Coach

- Log practice sessions
- Enter evaluations
- Verify player-entered stats

### League Admin

- Approve teams
- Override game logs

### Scout

- View VPP (public access)

### Parent

- Optional read-only access to child's data

## Development Roadmap

### Phase 1 (Current)

- [x] Django backend + API for game logs
- [x] Player stats tracking
- [x] Token transaction system
- [x] JWT/API key authentication
- [x] DigitalOcean deployment
- [x] Solana testnet integration

### Phase 2 (Planned)

- Chain of Trust implementation
- Leaderboards (stats, league, region, age group)
- Admin dashboard
- Token staking & governance
- NFT gear marketplace

## Implementation Notes

### Data Management

- Game logs are normalized (linked to teams, players, events)
- Solana interactions are async with `transaction_hash` references
- Support for CSV import of box scores
- DRF ViewSets for API endpoints
- Mobile-first UX design

### Current State

The project currently implements:

- League and division management
- Team and player profiles
- Game logging and statistics
- Performance evaluations
- Coach-player interactions
- Basic authentication and authorization

### Next Steps

1. Web3 Integration

   - Token reward system
   - NFT achievement tracking
   - Solana wallet integration
   - Transaction management

2. Enhanced Privacy

   - Granular access control
   - Parent-child relationships
   - Data visibility settings

3. Performance Optimization
   - Stats/leaderboard caching
   - Async blockchain operations
   - Mobile API optimization

## API Endpoints

### Game Management

```
POST /api/v1/game/log
GET /api/v1/game/{game_id}
GET /api/v1/game/stats/{player_id}
```

### Player Management

```
GET /api/v1/player/stats/{player_id}
GET /api/v1/player/profile/{player_id}
POST /api/v1/player/evaluation
```

### Token Management

```
POST /api/v1/token/transfer
GET /api/v1/token/balance/{wallet_address}
```

### NFT Management

```
POST /api/v1/nft/mint
GET /api/v1/nft/achievements/{player_id}
```

## Contributing

Please refer to the project's contribution guidelines for information on how to contribute to this project.

## License

[License information to be added]
