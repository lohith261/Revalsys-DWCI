import { useState } from 'react';
import { v4 as uuidv4 } from 'uuid';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import { Message, UploadedFile } from './types';

export default function App() {
  const [sessionId, setSessionId] = useState(() => uuidv4());
  const [restoredMessages, setRestoredMessages] = useState<Message[]>([]);
  const [restoredFiles, setRestoredFiles] = useState<UploadedFile[]>([]);

  const handleNewChat = () => {
    setSessionId(uuidv4());
    setRestoredMessages([]);
    setRestoredFiles([]);
  };

  const handleChangeSession = (id: string) => {
    setSessionId(id);
    setRestoredMessages([]);
    setRestoredFiles([]);
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      <Sidebar
        currentSessionId={sessionId}
        onChangeSession={handleChangeSession}
        onNewChat={handleNewChat}
        onLoadMessages={setRestoredMessages}
        onLoadFiles={setRestoredFiles}
      />
      <ChatWindow
        sessionId={sessionId}
        onSessionChange={setSessionId}
        externalMessages={restoredMessages}
        uploadedFiles={restoredFiles}
      />
    </div>
  );
}
