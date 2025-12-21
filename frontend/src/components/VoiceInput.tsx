type Props = {
  onResult: (text: string) => void;
};

const VoiceInput = ({ onResult }: Props) => {
  const startListening = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Voice input not supported");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.start();

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      onResult(transcript);
    };
  };

  return (
    <button
      onClick={startListening}
      className="border px-3 py-2 rounded text-sm"
      title="Speak"
    >
      🎤
    </button>
  );
};

export default VoiceInput;
