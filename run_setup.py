import os
import sys
import subprocess
import time
import yaml
import psutil
import threading
import logging
from pathlib import Path
import webbrowser

class FraudDetectionSystem:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.processes = {}
        self.is_running = False
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('fraud_detection_system.log')
            ]
        )
        self.logger = logging.getLogger(__name__)

    def check_environment(self):
        """Check if all required components are present"""
        print("\n🔍 Checking system environment...")
        
        # Check required directories
        required_dirs = ['models', 'src', 'app', 'config']
        for dir_name in required_dirs:
            dir_path = self.root_dir / dir_name
            if not dir_path.exists():
                print(f"❌ Missing directory: {dir_name}")
                return False
            print(f"✅ Found directory: {dir_name}")

        # Check required files
        required_files = {
            'models': ['lstm_model.pth', 'cnn_model.pth', 'scaler.pkl', 'model_params.pkl'],
            'src': ['rules_engine.py', 'transaction_simulator.py', 'model_predictor.py', 'utils.py'],
            'app': ['routes.py'],  # Changed from main.py to routes.py
            'config': ['rules_config.yaml', 'app_config.yaml']
        }

        for dir_name, files in required_files.items():
            for file_name in files:
                file_path = self.root_dir / dir_name / file_name
                if not file_path.exists():
                    print(f"❌ Missing file: {dir_name}/{file_name}")
                    return False
                print(f"✅ Found file: {dir_name}/{file_name}")

        print("\n✅ Environment check completed successfully!")
        return True

    def check_dependencies(self):
        """Check if all required Python packages are installed"""
        print("\n🔍 Checking dependencies...")
        
        required_packages = [
            'flask',  # Changed from streamlit to flask
            'pandas',
            'numpy',
            'torch',
            'joblib',
            'pyyaml',
            'plotly',
            'scikit-learn'
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ Found package: {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ Missing package: {package}")

        if missing_packages:
            print("\n⚠️ Installing missing packages...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ All packages installed successfully!")

        return True

    def start_flask(self):
        """Start Flask application"""
        print("\n🚀 Starting Flask server...")
        try:
            flask_script = """
from app import create_app
app = create_app()
app.run(debug=True, port=5000)
"""
            # Write temporary script
            with open('start_flask.py', 'w') as f:
                f.write(flask_script)

            # Start Flask in a separate process
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.root_dir)
            
            self.processes['flask'] = subprocess.Popen(
                [sys.executable, 'start_flask.py'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(2)
            if self.processes['flask'].poll() is None:
                print("✅ Flask server started successfully!")
                webbrowser.open('http://localhost:5000')
                return True
            else:
                error = self.processes['flask'].stderr.read().decode()
                print(f"❌ Failed to start Flask server: {error}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting Flask: {str(e)}")
            return False
        finally:
            # Clean up temporary script
            if os.path.exists('start_flask.py'):
                os.remove('start_flask.py')

    def start_transaction_simulator(self):
        """Start transaction simulator"""
        print("\n🚀 Starting transaction simulator...")
        
        try:
            # Create/update simulator script
            simulator_path = self.create_simulator_script()
            
            # Set Python path to include project root
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.root_dir)
            
            # Start simulator process
            self.processes['simulator'] = subprocess.Popen(
                [sys.executable, str(simulator_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            time.sleep(2)
            if self.processes['simulator'].poll() is None:
                def monitor_output():
                    while True:
                        output = self.processes['simulator'].stdout.readline()
                        if output:
                            print(f"Simulator: {output.strip()}")
                        else:
                            break
                
                threading.Thread(target=monitor_output, daemon=True).start()
                
                print("✅ Transaction simulator started successfully!")
                return True
            else:
                error_output = self.processes['simulator'].stderr.read()
                print(f"❌ Failed to start simulator: {error_output}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting simulator: {str(e)}")
            return False

    def monitor_processes(self):
        """Monitor running processes"""
        while self.is_running:
            for name, process in self.processes.items():
                if process.poll() is not None:
                    print(f"\n⚠️ {name} process stopped! Restarting...")
                    if name == 'flask':
                        self.start_flask()
                    elif name == 'simulator':
                        self.start_transaction_simulator()
            time.sleep(5)

    def start(self):
        """Start the entire system"""
        print("\n🚀 Starting Fraud Detection System...")
        
        if not self.check_environment() or not self.check_dependencies():
            print("\n❌ System checks failed! Please fix the issues and try again.")
            return False

        if not self.start_flask() or not self.start_transaction_simulator():
            print("\n❌ Failed to start all components! Shutting down...")
            self.stop()
            return False

        self.is_running = True
        monitor_thread = threading.Thread(target=self.monitor_processes)
        monitor_thread.daemon = True
        monitor_thread.start()

        print("\n✅ Fraud Detection System started successfully!")
        print("\n📊 Dashboard available at: http://localhost:5000")
        print("\n⚠️ Press Ctrl+C to stop the system")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop all components"""
        print("\n🛑 Stopping Fraud Detection System...")
        
        self.is_running = False
        
        for name, process in self.processes.items():
            print(f"Stopping {name}...")
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

        print("✅ System stopped successfully!")

def create_app():
    """Factory function for creating Flask app"""
    from app.routes import main_bp
    
    app = Flask(__name__)
    app.register_blueprint(main_bp)
    return app

def main():
    system = FraudDetectionSystem()
    try:
        system.start()
    except KeyboardInterrupt:
        system.stop()
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        system.stop()

if __name__ == "__main__":
    main()