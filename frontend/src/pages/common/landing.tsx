import { useState } from "react";
import ChatMessage from "../../components/chatMessage";
import FileUploader from "../../components/FileUploader";
import VoiceInput from "../../components/VoiceInput";

type Message = {
  role: "user" | "assistant";
  content: string;
};

const CommonLanding = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async (text: string) => {
    if (!text.trim()) return;

    const newMessages: Message[] = [
  ...messages,
  { role: "user", content: text },
];

    setMessages(newMessages);
    setInput("");
    setLoading(true);

    // 🔗 Connect this to backend OpenAI / PDF chat API
    setTimeout(() => {
      setMessages([
        ...newMessages,
        {
          role: "assistant",
          content: "This is a sample AI response based on uploaded documents.",
        },
      ]);
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r p-4">
        <h2 className="text-xl font-semibold mb-4">Mediation Assistant</h2>
        <FileUploader />
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((msg, i) => (
            <ChatMessage key={i} message={msg} />
          ))}

          {loading && (
            <div className="text-gray-500 text-sm">AI is typing...</div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t bg-white p-4 flex items-center gap-2">
          <VoiceInput onResult={(text) => setInput(text)} />

          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage(input)}
            placeholder="Ask about your case or uploaded documents..."
            className="flex-1 border rounded px-4 py-2 focus:outline-none"
          />

          <button
            onClick={() => sendMessage(input)}
            className="bg-blue-600 text-white px-4 py-2 rounded"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default CommonLanding;
