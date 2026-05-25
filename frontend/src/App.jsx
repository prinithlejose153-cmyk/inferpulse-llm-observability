import { useEffect, useState } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";

function App() {
  const [activeTab, setActiveTab] = useState("chat");
  const [message, setMessage] = useState("");
  const [chatMessages, setChatMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);

  const [summary, setSummary] = useState(null);
  const [logs, setLogs] = useState([]);

  const fetchConversations = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/conversations`);
      setConversations(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  const loadConversation = async (id) => {
    try {
      const response = await axios.get(`${API_BASE}/api/conversations/${id}`);

      setConversationId(response.data.id);
      setChatMessages(response.data.messages);
      setActiveTab("chat");
    } catch (error) {
      console.error(error);
    }
  };

  const fetchDashboard = async () => {
    try {
      const [summaryRes, logsRes] = await Promise.all([
        axios.get(`${API_BASE}/api/dashboard/summary`),
        axios.get(`${API_BASE}/api/dashboard/recent-logs`),
      ]);

      setSummary(summaryRes.data);
      setLogs(logsRes.data);
    } catch (error) {
      console.error(error);
    }
  };

  const sendMessage = async () => {
    if (!message.trim()) return;

    const userText = message;

    setChatMessages((prev) => [...prev, { role: "user", content: userText }]);
    setMessage("");
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/api/chat`, {
        message: userText,
        conversation_id: conversationId,
      });

      setConversationId(response.data.conversation_id);

      setChatMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.data.reply },
      ]);

      fetchDashboard();
      fetchConversations();
    } catch (error) {
      setChatMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Error: failed to get assistant response.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const startNewConversation = () => {
    setConversationId(null);
    setChatMessages([]);
    setMessage("");
  };

  const cancelConversation = async () => {
    if (!conversationId) {
      startNewConversation();
      return;
    }

    try {
      await axios.delete(`${API_BASE}/api/conversations/${conversationId}`);
      startNewConversation();
      fetchConversations();
      fetchDashboard();
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchDashboard();
    fetchConversations();
  }, []);

  const latencyData = logs
    .slice()
    .reverse()
    .map((log, index) => ({
      name: `Req ${index + 1}`,
      latency: log.latency_ms,
    }));

  return (
    <div className="app">
      <aside className="sidebar">
        <h1>InferPulse</h1>
        <p>LLM Inference Observability</p>

        <button
          className={activeTab === "chat" ? "active" : ""}
          onClick={() => setActiveTab("chat")}
        >
          Chatbot
        </button>

        <button
          className={activeTab === "dashboard" ? "active" : ""}
          onClick={() => {
            setActiveTab("dashboard");
            fetchDashboard();
          }}
        >
          Dashboard
        </button>

        <div className="conversation-list">
          <h3>Conversations</h3>

          {conversations.length === 0 && (
            <p className="small-muted">No conversations yet</p>
          )}

          {conversations.map((conversation) => (
            <button
              key={conversation.id}
              className={
                conversationId === conversation.id
                  ? "active conversation-btn"
                  : "conversation-btn"
              }
              onClick={() => loadConversation(conversation.id)}
            >
              {conversation.title || "Untitled"}
            </button>
          ))}
        </div>
      </aside>

      <main className="main">
        {activeTab === "chat" ? (
          <section className="panel">
            <div className="panel-header">
              <div>
                <h2>Chatbot</h2>
                <p>Multi-turn chatbot with SDK-based inference logging.</p>
              </div>

              <div className="header-actions">
                <button className="secondary" onClick={startNewConversation}>
                  New Conversation
                </button>

                <button className="danger" onClick={cancelConversation}>
                  Cancel Conversation
                </button>
              </div>
            </div>

            <div className="chat-window">
              {chatMessages.length === 0 && (
                <div className="empty-state">
                  Ask something to generate an inference log.
                </div>
              )}

              {chatMessages.map((msg, index) => (
                <div key={index} className={`message ${msg.role}`}>
                  <strong>{msg.role === "user" ? "You" : "Assistant"}</strong>
                  <p>{msg.content}</p>
                </div>
              ))}

              {loading && <div className="loading">Generating response...</div>}
            </div>

            <div className="input-row">
              <input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") sendMessage();
                }}
                placeholder="Type your message..."
              />
              <button onClick={sendMessage} disabled={loading}>
                Send
              </button>
            </div>
          </section>
        ) : (
          <section className="panel">
            <div className="panel-header">
              <div>
                <h2>Inference Dashboard</h2>
                <p>Latency, throughput, token usage, and errors.</p>
              </div>

              <button className="secondary" onClick={fetchDashboard}>
                Refresh
              </button>
            </div>

            {summary && (
              <div className="metrics-grid">
                <Metric title="Total Requests" value={summary.total_requests} />
                <Metric title="Success Rate" value={`${summary.success_rate}%`} />
                <Metric
                  title="Avg Latency"
                  value={`${summary.average_latency_ms} ms`}
                />
                <Metric title="Total Tokens" value={summary.total_tokens} />
                <Metric title="Errors" value={summary.error_count} />
                <Metric
                  title="Providers"
                  value={Object.keys(summary.providers || {}).join(", ") || "N/A"}
                />
              </div>
            )}

            <div className="chart-card">
              <h3>Latency Trend</h3>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={latencyData}>
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="latency" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="logs-table">
              <h3>Recent Inference Logs</h3>

              <table>
                <thead>
                  <tr>
                    <th>Status</th>
                    <th>Provider</th>
                    <th>Model</th>
                    <th>Latency</th>
                    <th>Tokens</th>
                    <th>Input Preview</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => (
                    <tr key={log.id}>
                      <td>
                        <span className={`badge ${log.status}`}>
                          {log.status}
                        </span>
                      </td>
                      <td>{log.provider}</td>
                      <td>{log.model}</td>
                      <td>{log.latency_ms} ms</td>
                      <td>{log.total_tokens}</td>
                      <td>{log.input_preview}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

function Metric({ title, value }) {
  return (
    <div className="metric-card">
      <p>{title}</p>
      <h3>{value}</h3>
    </div>
  );
}

export default App;