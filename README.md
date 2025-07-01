# AI Gaming Assistant

An intelligent gaming assistant that provides real-time suggestions and analysis for popular competitive games like Valorant.

## Features

- Real-time game state analysis
- Customizable floating overlay
- Game-specific suggestions
- Automatic game detection
- Draggable and minimizable interface

## Supported Games

- Valorant


## Requirements

- Windows 10/11
- Python 3.11+
- GPU recommended for better performance



2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Select your game from the dropdown menu in the overlay window.

3. The overlay will automatically detect when your game is running and start providing suggestions.

4. You can drag the overlay window to reposition it on your screen.

5. Use the minimize button (_) to minimize the overlay when not needed.

## Features by Game

### Valorant
- Combat situation detection
- Utility usage suggestions
- Economy management tips


## Step-by-Step Workflow

1. **Screen Capture** (`GameStateDetector.capture_screen`)
   - Captures the current game window or full screen using Windows APIs and OpenCV.
   - This is the entry point for all downstream analysis, ensuring the assistant always works with the latest game frame.

2. **Game State Extraction** (`GameStateDetector.process_frame` and `_get_valorant_state`)
   - Processes the captured frame to extract structured game state information (combat, abilities, equipped gun, etc.).
   - Uses computer vision to detect combat and other HUD elements, ensuring context-aware suggestions.

3. **Rule-Based Suggestion Pipeline** (`AISuggestionPipeline`)
   - Filters and prioritizes suggestions based on the current game state using nested condition checks.
   - Ensures only relevant tips (e.g., ability usage) are shown when their conditions are met (e.g., Q/E only in combat).

4. **ML/Neural Network Suggestions** (`ValorantGameModel`)
   - Optionally uses a neural network to provide additional suggestions based on the structured state.
   - Integrates with the rule-based pipeline for hybrid advice.

5. **Vision-Language Model Suggestions** (`ValorantVisionAISuggester`)
   - Uses the BLIP model to generate natural language suggestions directly from the game screen.
   - Adds a layer of visual context-awareness, especially when rule-based or ML logic is uncertain.

6. **Suggestion Aggregation and Prioritization**
   - Combines rule-based, ML, and vision AI suggestions, sorts by priority, and selects the top 3 for display.

7. **Overlay Display** (`OverlayWindow`)
   - Updates the floating overlay with the latest suggestions, styled by priority.
   - Handles user interaction (drag, minimize, settings) and ensures non-intrusive, real-time feedback.

8. **Session Logging** (`GameDataCollector`)
   - Records all game states and suggestions for later review, debugging, or model training.

## Importance of Key Functions and Modules

- **backend/game_state.py**: Core for extracting real-time game state from the screen. Functions like `_detect_combat` and `_detect_abilities` ensure suggestions are context-aware.

- **backend/ai_pipeline.py**: Filters and matches suggestions to the current state, supporting nested and complex conditions.

- **backend/suggestion_models.py**: Defines all rule-based suggestions and their conditions for each game.

- **ml/models/valorant_model.py**: Provides ML-based suggestions using structured state as input.

- **ml/models/valorant_vision_ai.py**: Integrates the BLIP vision-language model for visual context suggestions.

- **overlay/overlay_window.py**: Manages the user interface, displaying suggestions and handling user actions.

- **main.py**: Orchestrates the workflow, calling all modules in sequence and updating the overlay in real time.

- **backend/utils/config.py**: Stores all configuration for screen regions, HUD elements, and game-specific settings.

- **ml/utils/data_collector.py**: Handles session data logging for analytics and future improvements.

This modular design ensures the AI-Gaming Assistant is robust, extensible, and delivers highly relevant, real-time advice to players.

## Customization

You can customize various settings in `backend/utils/config.py`:
- Screen capture settings
- Overlay appearance
- Update intervals
- Game-specific configurations

## Contributing

Feel free to contribute to this project by:
1. Reporting bugs
2. Suggesting new features
3. Submitting pull requests

Abstract:
Abstract
The AI-Gaming Assistant is a real-time, context-aware overlay system designed to enhance player performance in Valorant by providing actionable, situation-specific suggestions. Leveraging computer vision, machine learning, and advanced vision-language models (BLIP), the assistant continuously analyzes the game screen to detect key gameplay states such as combat engagement, ability availability, and equipped weapon. The system ensures that ability-related suggestions (e.g., using Q or E) are only shown when the player is actively in combat, increasing the relevance and accuracy of the advice. The overlay displays the top prioritized suggestions, combining rule-based logic, neural network outputs, and BLIP-generated vision AI tips. This hybrid approach ensures that players receive both tactical and strategic guidance tailored to the current in-game context. The assistant is modular, extensible, and designed for seamless integration with the Valorant HUD, providing a non-intrusive yet highly informative user experience.