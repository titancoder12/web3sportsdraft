
# Technical Specification & Requirements Documentation

## 1. Overview
The Player Development Platform (PDP) is a Django-based web application for tracking youth baseball training, performance, and league management. It is designed as the foundation for a future Web3 Baseball Platform, with planned integration of tokens, NFTs, and blockchain-based data verification.

## 2. System Architecture

### 2.1 Tech Stack
- **Backend**: Django, Django REST Framework  
- **Database**: SQLite (dev), PostgreSQL (prod, planned)  
- **Frontend**: Django Templates (mobile-first UX)  
- **APIs**: RESTful endpoints via DRF  
- **Authentication**: Django Auth, JWT (planned), Token Auth, Solana Wallet (planned)  
- **Blockchain**: Solana (planned, partial integration)  
- **Infrastructure**: DigitalOcean, Celery (planned), Redis (planned)

## 3. Core Features

### 3.1 Game Logging
- Log games, teams, and player stats via web forms and CSV import.  
- **API**: `POST /api/v1/game/log`  
- Game data is normalized and linked to teams, players, and events.

### 3.2 Player Statistics
- Track and display player stats per game and in aggregate.  
- Stats must be verified by a coach/admin.  
- One stat record per player per game (enforced by unique constraint).

### 3.3 Coach Evaluations
- Structured performance evaluations submitted by coaches.  
- Metrics include grip strength, exit velocity, and notes.

### 3.4 Team & League Management
- Support for leagues, divisions, teams, and rosters.  
- Join requests, approvals, and draft management.  
- Admins can override logs and approve teams.

### 3.5 Token & NFT Integration (Planned)
- $BASEBALL token rewards for performance and engagement.  
- NFT achievements for milestones.  
- Verified Performance Profile (VPP) minted as NFT.

## 4. Data Model

### 4.1 Main Entities
- **League, Division, Team**: Hierarchical structure  
- **Player**: Linked to User, can belong to multiple teams  
- **Game**: Metadata including date, location  
- **PlayerGameStat**: Unique per (player, game)  
- **PerformanceEvaluation**: Coach evaluations  
- **DraftPick, TeamLog, PlayerLog, JoinTeamRequest, PlayerNote, PlayerJournalEntry**

### 4.2 Key Constraints
- **PlayerGameStat**: Unique per (player, game)  
- **JoinTeamRequest**: Unique per (player, team)

## 5. User Roles & Permissions
- **Player**: View/edit own stats (unverified), request to join teams  
- **Coach**: Log practices, verify stats, submit evaluations  
- **League Admin**: Approve teams, override logs  
- **Scout**: View public VPPs  
- **Parent**: Optional read-only access

## 6. Workflows

### 6.1 Stat Submission
- Players submit and edit their own unverified stats  
- Coaches verify stats (web or API)  
- Verified stats are immutable by players

### 6.2 CSV Import
- Admins/coaches upload box scores  
- Stats created/updated per unique constraint

### 6.3 Team Join Requests
- Players request team join  
- Coaches/admins approve/reject requests

### 6.4 Evaluations
- Coaches submit periodic evaluations  
- Players view history

## 7. API Endpoints

### Game Management
- `POST /api/v1/game/log`  
- `GET /api/v1/game/{game_id}`  
- `GET /api/v1/game/stats/{player_id}`

### Player Management
- `GET /api/v1/player/stats/{player_id}`  
- `GET /api/v1/player/profile/{player_id}`  
- `POST /api/v1/player/evaluation`

### Token/NFT Management (Planned)
- `POST /api/v1/token/transfer`  
- `GET /api/v1/token/balance/{wallet_address}`  
- `POST /api/v1/nft/mint`  
- `GET /api/v1/nft/achievements/{player_id}`

### Stat Verification
- `PATCH /api/v1/player/stats/{stat_id}/verify`

## 8. Security & Authentication
- Django Auth for web  
- Token Auth for API  
- JWT & Solana Wallet (planned)  
- Role-based permission checks

## 9. Requirements

### 9.1 Functional
- Register/login  
- Stat submission & verification  
- CSV import  
- REST API  
- Mobile-friendly UI

### 9.2 Non-Functional
- Data integrity  
- Security (auth, CSRF)  
- Scalable backend (PostgreSQL, Redis, Celery)  
- Modular for future Web3 features

## 10. Planned Features (Roadmap)
- Blockchain stat verification  
- Leaderboards & analytics  
- Parent/child account linking  
- Admin dashboard  
- NFT gear marketplace

## 11. Dependencies
- Django 5.1.3  
- djangorestframework 3.15.2  
- django-cors-headers, django-environ  
- asgiref, sqlparse, typing_extensions, wheel

## 12. Deployment
- DigitalOcean droplet  
- Static files in `/home/django-user/web3sportsdraft/static`  
- Environment vars via `.env`

## 13. Limitations
- Dev database is SQLite  
- Blockchain/token features are partially implemented  
- No parent/child linking yet  
- Admin dashboard is basic

## 14. References
- See `PROJECT_CONTEXT.md` for roadmap and APIs  
- See `README.md` for demo & links

## 15. Lineup Builder (Planned)

### 15.1 Overview
The Lineup Builder is a planning and compliance tool for coaches to construct batting orders and defensive rotations. It assists in managing grassroots-level fair play rules (e.g., innings played, position diversity), optimizing for both equity and competitiveness. It is built for mobile-first access on game day.

### 15.2 Key Functionalities
- **Roster Selection** – Exclude unavailable or injured players  
- **Batting Order** – Drag-and-drop interface, auto-generation options  
- **Defensive Rotation** – Assign positions by inning  
- **Fairness Engine** – Track innings played, catcher load, bench time  
- **Templates** – Save and reuse historical lineups, auto-adjust for absentees

### 15.3 Data Model Additions
- `LineupPlan`: team, game (optional), coach, timestamps  
- `LineupEntry`: player, batting_order, positions_by_inning (JSON)  
- `PlayerAvailability`: player, game, status (available, absent, late, injured)

### 15.4 API Endpoints (Planned)
- `POST /api/v1/lineup/plan` – Create a new plan  
- `GET /api/v1/lineup/plan/{team_id}` – Retrieve lineup  
- `PATCH /api/v1/lineup/entry/{entry_id}` – Update player entry  
- `GET /api/v1/lineup/history/{team_id}` – History

### 15.5 Permissions
- **Coach** – Full CRUD for team lineups  
- **Player** – View own slot (read-only)  
- **Admin** – Audit team fairness stats

### 15.6 Integration Notes
- Mobile-first UI  
- Ties into Player, Team, Game models  
- Future: Pull stats/evals for lineup suggestions  
- Pitch count and position compliance integration (optional)

## 16. FairPlay Rule Engine (Planned)

### 16.1 Overview
To comply with diverse fair play rules set by organizations such as BC Minor Baseball Association (BCMBA), PDP will include a modular FairPlay Rule Engine. This engine allows enforcement of dynamic constraints like minimum innings played, batting appearances, position limits, and bench rotations per league or age group.

### 16.2 FairPlay RuleSet Model

```python
class FairPlayRuleSet(models.Model):
    league = models.ForeignKey("League", on_delete=models.CASCADE)
    age_group = models.CharField(max_length=10)  # e.g., "11U"
    min_innings_per_player = models.IntegerField(default=0)
    max_consecutive_bench_innings = models.IntegerField(default=0)
    min_plate_appearances = models.IntegerField(default=0)
    enforce_plate_appearance = models.BooleanField(default=False)
    enforce_position_rotation = models.BooleanField(default=False)
    max_innings_per_position = JSONField(default=dict)  # e.g., {"C": 3, "P": 3}
    eh_option_start_date = models.DateField(null=True, blank=True)
    eh_option_end_date = models.DateField(null=True, blank=True)
    no_mandated_fair_play = models.BooleanField(default=False)
```

### 16.3 Sample Rules from BCMBA

- **10U & 11U**: All players must play 3 innings in a 6-inning game; no sitting two consecutive innings (summer).
- **13U A/AA/AAA**: Minimum 3 innings in 6–7 inning games, 2 innings in 5-inning games.
- **18U AA**: Must play 3 defensive outs and have one plate appearance.
- **15U/18U AAA**: No mandated fair play rules; acknowledgment form required.

### 16.4 Implementation Strategy

- Extend the `Game` model to include a reference to the assigned `FairPlayRuleSet`.
- During lineup planning, validate:
  - Innings played >= `min_innings_per_player`
  - No player benched for more than `max_consecutive_bench_innings`
  - Position counts against `max_innings_per_position`
  - At least `min_plate_appearances` if enforced
- Support for automatic warnings and inline UI validations in the Lineup Builder.
- Track historical lineup entries for compliance over time (e.g., check bench rotation patterns).

### 16.5 Compliance and Reporting

- Generate compliance status reports per game.
- Show rule violations directly in the lineup UI.
- Maintain audit logs for league admins.
