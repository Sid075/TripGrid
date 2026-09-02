# TripGrid 🌍

> **ML-powered group trip planning with intelligent recommendations and pooled budgets.**

TripGrid is an **ML-powered group travel recommendation system** that combines individual traveler preferences with a **pooled group budget** to identify, score, and rank destinations that best fit the entire group.

The system brings together **Machine Learning, preference aggregation, budget pooling, and group decision-making** to simplify the process of choosing a destination everyone can agree on.

---

## ✨ Key Features

### 🤖 ML-Powered Recommendations

TripGrid uses a **Machine Learning model** to evaluate destinations based on traveler preferences and destination characteristics.

The system predicts destination suitability and generates a ranked list of recommendations.

### 👥 Group Preference Aggregation

Each member can provide their own:

* 💰 Budget
* 🏖️ Travel type
* 📅 Trip duration
* 🎯 Preferred activities
* 🌤️ Preferred season

TripGrid combines these individual preferences to determine destinations that provide the best overall fit for the group.

### 💰 Budget Pooling

A key feature of TripGrid is **group budget pooling**.

Instead of treating every traveler's budget independently, the system calculates the **combined available budget of the entire group**.

```text
Member 1 Budget ─┐
Member 2 Budget ─┤
Member 3 Budget ─┼──→ Pooled Group Budget
Member 4 Budget ─┘
                         │
                         ▼
                 Destination Filtering
                         │
                         ▼
                  ML Recommendation
```

This allows the recommendation system to consider destinations that are financially feasible for the **group as a whole**.

### 🗳️ Group Decision Making

After generating recommendations, the shortlisted destinations can be presented to group members for voting.

```text
Individual Preferences
          ↓
Preference Aggregation
          ↓
Budget Pooling
          ↓
Destination Filtering
          ↓
ML Suitability Prediction
          ↓
Destination Ranking
          ↓
Group Voting
          ↓
     Final Destination
```

---

## 🧠 Machine Learning

TripGrid uses a **Random Forest Regressor** for destination suitability prediction.

The model learns relationships between destination characteristics and traveler preferences to estimate how suitable a destination is for the group.

### ML Pipeline

```text
Tourism Dataset
      ↓
Data Cleaning
      ↓
Feature Engineering
      ↓
Categorical Encoding
      ↓
Train / Test Split
      ↓
Random Forest Regressor
      ↓
Suitability Prediction
      ↓
Destination Ranking
```

### Why Random Forest?

Random Forest was selected because it:

* Handles nonlinear relationships
* Works well with structured/tabular data
* Handles multiple input features
* Is relatively robust to noise
* Can model interactions between different preferences
* Provides feature importance

---

## 💻 SDK / Application Layer

TripGrid is designed with an **SDK/API-driven application layer** that connects the user-facing trip-planning workflow with the recommendation and decision-making logic.

The SDK layer can be used to:

* Submit group member preferences
* Process and aggregate travel requirements
* Calculate the pooled group budget
* Request destination recommendations
* Retrieve ranked destinations
* Support group voting and final destination selection

This separation makes the recommendation engine easier to integrate into different interfaces or applications.

```text
┌──────────────────────────┐
│       User Interface     │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│       SDK / API Layer    │
└────────────┬─────────────┘
             │
      ┌──────┴───────┐
      ▼              ▼
┌─────────────┐ ┌──────────────┐
│ Budget Pool │ │ Preferences  │
└──────┬──────┘ └──────┬───────┘
       │               │
       └───────┬───────┘
               ▼
      ┌─────────────────┐
      │ ML Recommendation│
      │     Engine       │
      └────────┬────────┘
               ▼
      ┌─────────────────┐
      │ Ranked Destinations│
      └────────┬────────┘
               ▼
        Group Decision
```

---

## 🛠️ Tech Stack

### Machine Learning

* Python
* Pandas
* NumPy
* Scikit-learn
* Random Forest Regressor

### Recommendation System

* Preference aggregation
* Budget pooling
* Destination filtering
* Suitability prediction
* Destination ranking

### Application / Integration

* SDK / API layer
* Modular recommendation engine

---

## 🎯 Core Concept

TripGrid solves a common group-travel problem:

> **How do multiple people with different preferences and budgets find a destination that works for everyone?**

Instead of simply recommending destinations to individual users, TripGrid considers the **group as a whole**.

**Individual Preferences + Pooled Budget + ML Recommendation + Group Voting = TripGrid**

---

## 🚀 Future Improvements

* 🗺️ Real-time maps and route planning
* ✈️ Live flight and transportation pricing
* 🏨 Hotel recommendations
* 💰 Dynamic trip-cost estimation
* 🌦️ Real-time weather integration
* 🤖 AI-generated itineraries
* 📱 Mobile application
* 👤 User profiles and preference history
* 📊 Explainable ML recommendations
* 🌐 Real-time travel APIs through the SDK
