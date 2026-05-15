import { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';
import { Send, Terminal, Monitor, Lock } from 'lucide-react';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

export default function RemoteControl() {
  const [password, setPassword] = useState('');
  const [isAuth, setIsAuth] = useState(false);
  const [command, setCommand] = useState('');
  const [logs, setLogs] = useState([]);
  const [screenshot, setScreenshot] = useState('');
  const [status, setStatus] = useState('Disconnected');

  useEffect(() => {
    if (isAuth) {
      const logSub = supabase.channel('logs').on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'logs' }, payload => {
        setLogs(prev => [payload.new, ...prev].slice(0, 50));
      }).subscribe();

      const stateSub = supabase.channel('state').on('postgres_changes', { event: 'UPDATE', schema: 'public', table: 'state' }, payload => {
        setScreenshot(payload.new.last_screenshot);
      }).subscribe();

      return () => {
        supabase.removeChannel(logSub);
        supabase.removeChannel(stateSub);
      };
    }
  }, [isAuth]);

  const handleLogin = () => {
    if (password === 'rayyan3mkidk') {
      setIsAuth(true);
    } else {
      alert('Wrong password');
    }
  };

  const sendCommand = async () => {
    if (!command) return;
    const { error } = await supabase.from('commands').insert([{ instruction: command, status: 'pending' }]);
    if (error) alert(error.message);
    else setCommand('');
  };

  if (!isAuth) {
    return (
      <div style={{ backgroundColor: '#121212', height: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'white', fontFamily: 'sans-serif' }}>
        <Lock size={48} style={{ marginBottom: 20, color: '#0070f3' }} />
        <h1>AI Remote Access</h1>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Enter Access Code"
          style={{ padding: 12, borderRadius: 8, border: 'none', width: '80%', maxWidth: 300, marginBottom: 20 }}
        />
        <button onClick={handleLogin} style={{ padding: '12px 24px', borderRadius: 8, border: 'none', backgroundColor: '#0070f3', color: 'white', fontWeight: 'bold' }}>UNLOCK</button>
      </div>
    );
  }

  return (
    <div style={{ backgroundColor: '#000', color: '#fff', minHeight: '100vh', padding: 15, fontFamily: 'sans-serif' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h2 style={{ margin: 0 }}>Peak AI Control</h2>
        <span style={{ fontSize: 12, color: '#444' }}>v1.0-Remote</span>
      </header>

      <section style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
          <Monitor size={18} /> <strong>Current PC View</strong>
        </div>
        <div style={{ width: '100%', height: 200, backgroundColor: '#111', borderRadius: 10, overflow: 'hidden', border: '1px solid #333' }}>
          {screenshot ? (
            <img src={`data:image/jpeg;base64,${screenshot}`} style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
          ) : (
            <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: '#555' }}>Waiting for screen...</div>
          )}
        </div>
      </section>

      <section style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 10 }}>
          <input
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            placeholder="Tell the AI what to do..."
            style={{ flex: 1, padding: 12, borderRadius: 8, border: 'none', backgroundColor: '#222', color: 'white' }}
          />
          <button onClick={sendCommand} style={{ padding: 12, borderRadius: 8, border: 'none', backgroundColor: '#0070f3', color: 'white' }}>
            <Send size={20} />
          </button>
        </div>
      </section>

      <section>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
          <Terminal size={18} /> <strong>Activity Log</strong>
        </div>
        <div style={{ height: 300, backgroundColor: '#111', borderRadius: 10, padding: 10, overflowY: 'auto', border: '1px solid #333', fontSize: 13 }}>
          {logs.map((log, i) => (
            <div key={i} style={{ marginBottom: 8, color: i === 0 ? '#0070f3' : '#aaa' }}>
              <span style={{ color: '#555' }}>[{new Date(log.created_at).toLocaleTimeString()}]</span> {log.message}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
