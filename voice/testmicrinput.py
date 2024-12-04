import speech_recognition as sr

recognizer = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something...")
    audio = recognizer.listen(source)
    print("Processing audio...")
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
    except sr.UnknownValueError:
        print("Sorry, I could not understand your speech.")
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
