import pyttsx3

# Initialize TTS engine
engine = pyttsx3.init()

# Function to speak a message
def speak(message):
    print(f"Speaking: {message}")
    engine.say(message)
    engine.runAndWait()

# Test TTS functionality
if __name__ == "__main__":
    speak("Testing Text to Speech. Hello, this is SoleMate.")
    speak("The system is working perfectly.")
