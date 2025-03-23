
# 🧠 Player Development Dashboard Overview

This document outlines the features and structure of the Player Dashboard focused on player development.

---

## ✅ Core Features (MVP)

### 1. 📅 Game History
- List of games the player has participated in
- Includes:
  - Opponent team
  - Date and location
  - Final score
  - Link to boxscore (e.g., /boxscore/<game_id>/)

### 2. 📊 Player Stats
- **Overall Stats**: Aggregated across all teams and games
- **Per-Team Stats**: Filtered by each team
- Stats include:
  - Games played
  - Hits, runs, RBIs, HRs, walks
  - Batting average, OBP, SLG
  - Pitching stats: IP, ERA, K/BB ratio

### 3. 📈 Progress Over Time (Graphs)
- Time-based visualization of key performance metrics:
  - Batting average
  - Strikeout rate
  - Exit velocity
  - Pop time, sprint time, throwing speed

### 4. 🧪 Evaluation Metrics
- Static combine-style data recorded at tryouts or training:
  - Grip strength
  - 5-10-5 shuttle
  - 10-yard dash
  - Exit velo
  - Bat speed
  - Catcher pop time
  - Fielding notes
  - Pitching comment

### 5. 📝 Coach Feedback (read-only for players)
- Display all feedback left by coaches:
  - Date
  - Coach name
  - Context (game, practice, training)
  - Comments
  - Optional: numeric rating (1–5 scale)
- Displayed in descending order (most recent first)

---

## 🧱 Backend Structure

### Views
- `player_dashboard(request)` — view for logged-in player

### URL
```python
path('dashboard/', views.player_dashboard, name='player_dashboard')
```

### Template
- `templates/player_dashboard.html`

---

## 🔮 Future Enhancements

### 🧑‍🏫 Coach Dashboard
- Coaches will be able to:
  - See teams they've coached
  - View players they've worked with
  - Leave feedback on games, practices, or training

### 🧭 Development Goals (Future)
- Coach or player-defined goals (e.g. “Raise OBP by 0.050”)
- Show progress and relevant stats over time

---

## 🧰 Models to Add

### `PlayerFeedback` model (new)
```python
class PlayerFeedback(models.Model):
    player = models.ForeignKey("Player", on_delete=models.CASCADE, related_name="feedback")
    coach = models.ForeignKey(User, on_delete=models.CASCADE)
    context = models.CharField(max_length=50, choices=[("game", "Game"), ("practice", "Practice"), ("training", "Training")])
    game = models.ForeignKey("Game", null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField(auto_now_add=True)
    comment = models.TextField()
    rating = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-date']
```

---

This dashboard will help players reflect on performance, track their development, and stay motivated with feedback from coaches.
