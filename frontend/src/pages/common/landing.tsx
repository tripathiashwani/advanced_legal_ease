import { useState } from "react";
import ChatMessage from "../../components/chatMessage";
import FileUploader from "../../components/FileUploader";
import VoiceInput from "../../components/VoiceInput";
const BASE_AUTH_URL = "http://127.0.0.1:8001/api/accounts/"

type Message = {
  role: "user" | "assistant";
  content: string;
};

const CommonLanding = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return;

    setError(null);

    const userMessage: Message = {
      role: "user",
      content: text,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      console.log("Sending question to backend:", text);
      const res = await fetch(`${BASE_AUTH_URL}chat/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: text,
        }),
      });

      if (!res.ok) {
        throw new Error("Failed to get response from AI");
      }

      const data = await res.json();

      const aiMessage: Message = {
        role: "assistant",
        content: data.answer ?? "No response generated.",
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r p-4">
        <h2 className="text-xl font-semibold mb-4">
          Mediation Assistant
        </h2>

        <FileUploader />
        <p className="text-xs text-gray-500 mt-3">
          Upload case-related PDFs to ask questions from them.
        </p>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="text-gray-400 text-sm">
              Ask questions about uploaded case documents.
            </div>
          )}

          {messages.map((msg, i) => (
            <ChatMessage key={i} message={msg} />
          ))}

          {loading && (
            <div className="text-gray-500 text-sm">
              AI is typing...
            </div>
          )}

          {error && (
            <div className="text-red-500 text-sm">
              {error}
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t bg-white p-4 flex items-center gap-2">
          <VoiceInput onResult={(text) => setInput(text)} />

          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") sendMessage(input);
            }}
            placeholder="Ask about your case or uploaded documents..."
            className="flex-1 border rounded px-4 py-2 focus:outline-none"
            disabled={loading}
          />

          <button
            onClick={() => sendMessage(input)}
            disabled={loading}
            className={`px-4 py-2 rounded text-white ${
              loading
                ? "bg-blue-300 cursor-not-allowed"
                : "bg-blue-600"
            }`}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default CommonLanding;
