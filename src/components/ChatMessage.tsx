import React from "react";
import { Bot, User } from "lucide-react";
import { Message } from "../types";

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isAI = message.role === "ai";

  return (
    <div
      className={`flex items-start space-x-4 ${
        isAI ? "justify-start" : "justify-end"
      }`}
    >
      <div
        className={`flex max-w-[80%] ${
          isAI ? "flex-row" : "flex-row-reverse"
        } items-start space-x-4 ${
          isAI ? "bg-gray-50" : "bg-blue-50"
        } p-4 rounded-lg`}
      >
        <div
          className={`p-2 rounded-full ${
            isAI ? "bg-blue-100" : "bg-green-100"
          } ${isAI ? "mr-2" : "ml-2"}`}
        >
          {isAI ? (
            <Bot size={24} className="text-blue-600" />
          ) : (
            <User size={24} className="text-green-600" />
          )}
        </div>
        <div className="flex-1">
          <div className="font-medium mb-1">
            {isAI ? "AI Assistant" : "You"}
          </div>
          <p className="text-gray-700 whitespace-pre-wrap">{message.content}</p>
          <div className="text-xs text-gray-400 mt-1">
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
