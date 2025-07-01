import sys
import logging
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from backend.game_state import GameStateDetector
from backend.ai_pipeline import AISuggestionPipeline
from overlay.overlay_window import OverlayWindow
from ml.models.valorant_model import ValorantGameModel
from ml.models.valorant_vision_ai import ValorantVisionAISuggester
from ml.utils.data_collector import GameDataCollector

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main application entry point"""
    # Set up logging
    setup_logging()
    logger = logging.getLogger('main')
    
    # Initialize components
    app = QApplication(sys.argv)
    game_state = GameStateDetector('valorant')
    ai_pipeline = AISuggestionPipeline()
    ml_model = ValorantGameModel()
    vision_ai = ValorantVisionAISuggester()
    data_collector = GameDataCollector('valorant')
    overlay = OverlayWindow()
    overlay.show()

    def update():
        try:
            frame = game_state.capture_screen()
            if frame is None:
                logger.warning("Failed to capture screen")
                overlay.update_suggestions([])
                return
                
            state = game_state.process_frame(frame)
            logger.info(f"Current game state: {state}")
            
            # Log the new data points
            logger.info(f"Player health: {state.get('player_health')}")
            logger.info(f"Player armor: {state.get('player_armor')}")
            logger.info(f"Player position: {state.get('player_position')}")
            logger.info(f"Enemy positions: {state.get('enemy_positions')}")
            logger.info(f"Spike location: {state.get('spike_location')}")
            logger.info(f"Site control: {state.get('site_control')}")
            logger.info(f"Enemy presence: {state.get('enemy_presence')}")
            logger.info(f"Teammate with smoke: {state.get('teammate_with_smoke')}")
            logger.info(f"Teammate with flash: {state.get('teammate_with_flash')}")
            logger.info(f"Teammate with healing: {state.get('teammate_with_healing')}")
            logger.info(f"Need coordination: {state.get('need_coordination')}")
            
            data_collector.record_state(state)
            ml_predictions = ml_model.predict(state)

            # Get suggestions from AI pipeline (pass game name explicitly)
            suggestions = ai_pipeline.get_suggestions(state, game='valorant')
            logger.info(f"AI suggestions: {suggestions}")

            # Add ML predictions if available
            if ml_predictions and 'suggestions' in ml_predictions:
                suggestions.extend(ml_predictions['suggestions'])
                logger.info(f"ML suggestions: {ml_predictions['suggestions']}")

            # Add BLIP/vision AI suggestion
            try:
                vision_suggestion = vision_ai.suggest(frame)
                if vision_suggestion:
                    suggestions.append({
                        'id': 'blip_vision',
                        'text': f'Vision AI: {vision_suggestion}',
                        'priority': 2
                    })
                    logger.info(f"Vision AI suggestion: {vision_suggestion}")
            except Exception as e:
                logger.error(f"Vision AI error: {e}")

            # Update overlay with suggestions
            if suggestions:
                logger.info(f"Updating overlay with {len(suggestions)} suggestions")
                overlay.update_suggestions(suggestions)
            else:
                logger.info("No suggestions to display")
                overlay.update_suggestions([])
            
        except Exception as e:
            logger.error(f"Error in update: {e}")
            overlay.update_suggestions([])

    timer = QTimer()
    timer.timeout.connect(update)
    timer.start(100)  # Update every 100 ms

    try:
        sys.exit(app.exec())
    finally:
        # Clean up and save data
        if data_collector:
            try:
                data_collector.save_session()
            except Exception as e:
                logger.error(f"Error saving session data: {e}")
        logger.info("Application terminated")

if __name__ == "__main__":
    main()
