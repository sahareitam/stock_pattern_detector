# api/app.py
# Flask API implementation for Cup and Handle pattern detection

from flask import Flask, jsonify, request

from pattern_detector import get_detector
from config.config import STOCKS
from utils.logger import get_logger
from flask_cors import CORS

# Initialize logger
logger = get_logger(__name__)



def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    CORS(app)

    @app.route('/health', methods=['GET'])
    def health_check():
        """
        Health check endpoint to verify API is functioning correctly.

        Returns:
            JSON with status "ok" if API is healthy
        """
        logger.info("Health check request received")
        return jsonify({"status": "ok"})

    @app.route('/symbols', methods=['GET'])
    def get_symbols():
        """
        Get list of supported stock symbols.

        Returns:
            JSON with list of supported symbols from configuration
        """
        logger.info("Symbols list request received")
        return jsonify({"symbols": STOCKS})

    @app.route('/pattern/<symbol>', methods=['GET'])
    def check_pattern(symbol):
        """
        Check if Cup and Handle pattern exists for specified stock symbol.

        Args:
            symbol: Stock symbol to check (e.g., AAPL, MSFT)

        Returns:
            JSON with pattern_detected status (true/false)
        """
        # Log the request
        logger.info(f"Pattern check requested for symbol: {symbol}")

        # Validate the symbol
        if symbol not in STOCKS:
            logger.warning(f"Invalid symbol requested: {symbol}")
            return jsonify({"error": "Symbol not supported"}), 404

        try:
            # Get the pattern detector instance
            detector = get_detector()

            # Use the pattern detector to check for pattern
            # We use the default pattern_type "cup_and_handle"
            result = detector.detect_pattern(symbol=symbol)

            # Return the result
            logger.info(f"Pattern detection for {symbol}: {result}")
            return jsonify({"pattern_detected": result})

        except Exception as e:
            # Log the error and return 500
            logger.error(f"Error detecting pattern for {symbol}: {str(e)}", exc_info=True)
            return jsonify({"error": "Failed to detect pattern", "message": str(e)}), 500

    # Add another endpoint variation as an alternative path
    @app.route('/api/pattern', methods=['GET'])
    def check_pattern_query():
        """
        Check if Cup and Handle pattern exists for specified stock symbol using query parameter.

        Query Parameters:
            symbol: Stock symbol to check (e.g., AAPL, MSFT)

        Returns:
            JSON with pattern_detected status (true/false)
        """
        # Get the symbol from query parameters
        symbol = request.args.get('symbol')

        # Validate symbol parameter exists
        if not symbol:
            logger.warning("Symbol parameter missing in request")
            return jsonify({"error": "Symbol parameter is required"}), 400

        # Normalize the symbol (uppercase)
        symbol = symbol.upper()

        # Reuse the existing endpoint logic
        return check_pattern(symbol)

    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"Not found error: {error}")
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"Server error: {error}")
        return jsonify({"error": "Internal server error"}), 500

    return app


# Create a default app instance
flask_app = create_app()

def run_api_production(host="localhost", port=5000):
    """Run the Flask API with a production WSGI server."""
    import waitress
    logger.info(f"Starting API server with waitress on {host}:{port}")
    waitress.serve(flask_app, host=host, port=port)

def run_api(host="localhost", port=5000, debug=False):
    """
    Run the Flask API server.

    Args:
        host: Hostname to listen on (default: localhost)
        port: Port to listen on (default: 5000)
        debug: Enable debug mode (default: False)

    Returns:
        None
    """
    logger.info(f"Starting API server on {host}:{port}")
    flask_app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    # When run directly, start the API
    from config.config import API

    run_api(
        host=API.get("host", "localhost"),
        port=API.get("port", 5000),
        debug=API.get("debug", False)
    )