import React, { useState, useEffect } from 'react';
import { supabase } from './supabaseClient';
import Auth from './components/Auth';
import EmotionRecorder from './EmotionRecorder';
import Dashboard from './components/Dashboard';
import Profile from './components/Profile'; 
import Statistics from './components/Statistics';
import { theme } from './theme';
import bgImage from './assets/background.png';

function App() {
  const [session, setSession] = useState(null);
  const [view, setView] = useState('recorder'); // 'recorder', 'dashboard', 'statistics' або 'profile'

  useEffect(() => {
    // Отримуємо поточну сесію при завантаженні
    supabase.auth.getSession().then(({ data: { session } }) => setSession(session));
    
    // Слухаємо зміни стану авторизації (вхід/вихід)
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  // Функція для стилізації активних/неактивних кнопок навігації
  const navButtonStyle = (isActive) => ({
    background: isActive ? theme.colors.primary : 'transparent',
    color: isActive ? theme.colors.primaryDark : 'white',
    border: `1px solid ${theme.colors.primary}`,
    padding: '8px 20px',
    borderRadius: '20px',
    cursor: 'pointer',
    fontWeight: isActive ? 'bold' : 'normal',
    transition: theme.transition
  });

  if (!session) return <Auth />;

  return (
    <div className="App" style={{ minHeight: '100vh', backgroundImage: `url(${bgImage})`, ...theme.backgroundConfig, color: 'white' }}>
      {/* Навігаційна панель */}
      <nav style={{ 
        padding: '20px', 
        display: 'flex', 
        justifyContent: 'center', 
        flexWrap: 'wrap', // Щоб кнопки не "вилізали" на мобільних
        gap: '15px', 
        background: theme.colors.buttonCard,
        boxShadow: '0 4px 15px rgba(0,0,0,0.2)' 
      }}>
        <button 
          onClick={() => setView('recorder')} 
          style={navButtonStyle(view === 'recorder')}
        >
          Записати
        </button>
        
        <button 
          onClick={() => setView('dashboard')} 
          style={navButtonStyle(view === 'dashboard')}
        >
          Мої записи
        </button>

        <button 
          onClick={() => setView('statistics')} 
          style={navButtonStyle(view === 'statistics')}
        >
          Статистика
        </button>

        <button 
          onClick={() => setView('profile')} 
          style={navButtonStyle(view === 'profile')}
        >
          Профіль
        </button>

        <button 
          onClick={() => supabase.auth.signOut()} 
          style={{ 
            background: theme.colors.danger, 
            border: 'none', 
            color: 'white', 
            padding: '8px 20px', 
            borderRadius: '20px', 
            cursor: 'pointer',
            marginLeft: '10px'
          }}
        >
          Вийти
        </button>
      </nav>

      {/* Контент сторінок залежно від обраної вкладки */}
      <main style={{ padding: '20px' }}>
        {view === 'recorder' && <EmotionRecorder user={session.user} />}
        {view === 'dashboard' && <Dashboard user={session.user} />}
        {view === 'statistics' && <Statistics user={session.user} />}
        {view === 'profile' && <Profile user={session.user} />}
      </main>
    </div>
  );
}

export default App;